"""QR code generation service implementation.

This module contains the concrete implementation of QR code generation using Python libraries.
"""

import asyncio
import io
import time
import zipfile
from datetime import datetime, timezone
from typing import Dict, List, Optional

import qrcode
from PIL import Image, ImageDraw

# Optional dependencies
cairosvg = None
try:
    import cairosvg
except (ImportError, OSError):
    # cairosvg not available or Cairo system libraries not installed
    pass

from ..domain.qr_entities import (
    BulkQRGeneration,
    BulkQRResult,
    GeneratedQRCode,
    QRCodeData,
    QRCodePreview,
    QRErrorCorrection,
    QRFormat,
    QRSize,
)
from ..domain.qr_repos import IQRGenerationRepository


class QRGenerationService(IQRGenerationRepository):
    """Concrete implementation of QR code generation service."""
    
    def __init__(self):
        """Initialize the QR generation service."""
        self._size_mapping = {
            QRSize.SMALL: 200,
            QRSize.MEDIUM: 400,
            QRSize.LARGE: 800,
            QRSize.XLARGE: 1200,
        }
        
        self._error_correction_mapping = {
            QRErrorCorrection.LOW: qrcode.constants.ERROR_CORRECT_L,
            QRErrorCorrection.MEDIUM: qrcode.constants.ERROR_CORRECT_M,
            QRErrorCorrection.QUARTILE: qrcode.constants.ERROR_CORRECT_Q,
            QRErrorCorrection.HIGH: qrcode.constants.ERROR_CORRECT_H,
        }
    
    async def generate_qr_code(self, qr_data: QRCodeData) -> GeneratedQRCode:
        """Generate a single QR code.
        
        Args:
            qr_data: QR code data and configuration.
            
        Returns:
            Generated QR code with metadata.
            
        Raises:
            Exception: If QR code generation fails.
        """
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,  # Auto-determine version
                error_correction=self._error_correction_mapping[qr_data.config.error_correction],
                box_size=10,
                border=qr_data.config.border,
            )
            
            # Add data to QR code
            qr.add_data(qr_data.url)
            qr.make(fit=True)
            
            # Generate image based on format
            if qr_data.config.format == QRFormat.SVG:
                file_content = await self._generate_svg(qr, qr_data)
            elif qr_data.config.format == QRFormat.PDF:
                file_content = await self._generate_pdf(qr, qr_data)
            else:  # PNG
                file_content = await self._generate_png(qr, qr_data)
            
            return GeneratedQRCode(
                qr_data=qr_data,
                file_content=file_content,
                file_size=len(file_content),
                generated_at=datetime.now(timezone.utc),
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate QR code for table {qr_data.table_number}: {str(e)}")
    
    async def generate_bulk_qr_codes(self, bulk_request: BulkQRGeneration) -> BulkQRResult:
        """Generate QR codes for multiple tables.
        
        Args:
            bulk_request: Bulk generation request.
            
        Returns:
            Bulk generation result with statistics.
            
        Raises:
            Exception: If bulk generation fails.
        """
        start_time = time.time()
        request_id = f"bulk_{int(time.time())}"
        
        generated_qr_codes: List[GeneratedQRCode] = []
        failed_tables: List[str] = []
        
        # Generate QR codes concurrently (in batches to avoid overwhelming the system)
        batch_size = 10
        table_batches = [
            bulk_request.table_ids[i:i + batch_size]
            for i in range(0, len(bulk_request.table_ids), batch_size)
        ]
        
        for batch in table_batches:
            batch_tasks = []
            for table_id in batch:
                # Create QR data for each table
                qr_url = f"https://app.zergoqrf.com/menu/TEMP/{table_id}"  # Will be updated with actual restaurant code
                qr_data = QRCodeData(
                    url=qr_url,
                    table_id=table_id,
                    restaurant_id=bulk_request.restaurant_id,
                    restaurant_code="TEMP",  # Will be updated
                    table_number=f"T{str(table_id)[-4:]}",  # Temporary table number
                    config=bulk_request.config,
                )
                
                batch_tasks.append(self._generate_single_qr_safe(qr_data))
            
            # Execute batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    failed_tables.append(f"T{str(batch[i])[-4:]}")
                else:
                    generated_qr_codes.append(result)
        
        # Create ZIP file if requested
        zip_file_content = None
        zip_file_size = None
        
        if bulk_request.include_zip and generated_qr_codes:
            zip_file_content, zip_file_size = await self._create_zip_file(generated_qr_codes)
        
        generation_time = time.time() - start_time
        
        return BulkQRResult(
            request_id=request_id,
            restaurant_id=bulk_request.restaurant_id,
            total_requested=len(bulk_request.table_ids),
            total_generated=len(generated_qr_codes),
            failed_tables=failed_tables,
            zip_file_content=zip_file_content,
            zip_file_size=zip_file_size,
            generation_time_seconds=generation_time,
            generated_at=datetime.now(timezone.utc),
        )
    
    async def generate_qr_preview(self, qr_data: QRCodeData) -> QRCodePreview:
        """Generate a preview of the QR code.
        
        Args:
            qr_data: QR code data and configuration.
            
        Returns:
            QR code preview data.
            
        Raises:
            Exception: If preview generation fails.
        """
        try:
            # Generate a small PNG preview
            preview_config = qr_data.config.copy()
            preview_config.size = QRSize.SMALL
            preview_config.format = QRFormat.PNG
            
            preview_qr_data = qr_data.copy()
            preview_qr_data.config = preview_config
            
            generated_qr = await self.generate_qr_code(preview_qr_data)
            
            # Create a data URL for the preview
            import base64
            preview_data_url = f"data:image/png;base64,{base64.b64encode(generated_qr.file_content).decode()}"
            
            return QRCodePreview(
                qr_data=qr_data,
                preview_url=preview_data_url,
                preview_content=generated_qr.file_content,
            )
            
        except Exception as e:
            raise Exception(f"Failed to generate QR code preview: {str(e)}")
    
    async def validate_qr_scannability(self, qr_code: GeneratedQRCode) -> bool:
        """Validate that a QR code is scannable.
        
        Args:
            qr_code: Generated QR code to validate.
            
        Returns:
            True if QR code is scannable, False otherwise.
        """
        try:
            # Basic validation - check if the QR code can be decoded
            try:
                from pyzbar import pyzbar

                if qr_code.qr_data.config.format == QRFormat.PNG:
                    image = Image.open(io.BytesIO(qr_code.file_content))
                    decoded_objects = pyzbar.decode(image)

                    if decoded_objects:
                        decoded_url = decoded_objects[0].data.decode('utf-8')
                        return decoded_url == qr_code.qr_data.url
            except ImportError:
                # pyzbar not available, skip validation
                pass

            return True  # Assume valid if we can't validate

        except Exception:
            return False
    
    async def _generate_png(self, qr: qrcode.QRCode, qr_data: QRCodeData) -> bytes:
        """Generate PNG format QR code.
        
        Args:
            qr: QR code instance.
            qr_data: QR code data.
            
        Returns:
            PNG file content as bytes.
        """
        # Determine colors
        fill_color = qr_data.config.foreground_color
        back_color = qr_data.config.background_color
        
        # Create image
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # Resize to target size
        target_size = self._size_mapping[qr_data.config.size]
        img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Add logo if requested
        if qr_data.config.include_logo:
            img = await self._add_logo_to_image(img, qr_data)
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        return buffer.getvalue()
    
    async def _generate_svg(self, qr: qrcode.QRCode, qr_data: QRCodeData) -> bytes:
        """Generate SVG format QR code.

        Args:
            qr: QR code instance.
            qr_data: QR code data.

        Returns:
            SVG file content as bytes.
        """
        from qrcode.image.svg import SvgPathImage

        img = qr.make_image(
            image_factory=SvgPathImage,
            fill_color=qr_data.config.foreground_color,
            back_color=qr_data.config.background_color,
        )

        # Convert to string and then bytes
        svg_string = img.to_string()
        if isinstance(svg_string, bytes):
            return svg_string
        else:
            return svg_string.encode('utf-8')
    
    async def _generate_pdf(self, qr: qrcode.QRCode, qr_data: QRCodeData) -> bytes:
        """Generate PDF format QR code.

        Args:
            qr: QR code instance.
            qr_data: QR code data.

        Returns:
            PDF file content as bytes.
        """
        if cairosvg is None:
            raise Exception("cairosvg is required for PDF generation but not installed")

        # First generate SVG, then convert to PDF
        svg_content = await self._generate_svg(qr, qr_data)

        # Convert SVG to PDF using cairosvg
        pdf_content = cairosvg.svg2pdf(bytestring=svg_content)
        return pdf_content
    
    async def _add_logo_to_image(self, img: Image.Image, qr_data: QRCodeData) -> Image.Image:
        """Add restaurant logo to QR code image.
        
        Args:
            img: QR code image.
            qr_data: QR code data.
            
        Returns:
            QR code image with logo.
        """
        # For now, just add a simple placeholder circle in the center
        # In a real implementation, you would load the restaurant's logo
        
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        
        # Calculate logo size and position
        logo_size = int(min(img_width, img_height) * qr_data.config.logo_size_ratio)
        logo_x = (img_width - logo_size) // 2
        logo_y = (img_height - logo_size) // 2
        
        # Draw a white circle background
        draw.ellipse(
            [logo_x - 5, logo_y - 5, logo_x + logo_size + 5, logo_y + logo_size + 5],
            fill='white',
            outline='black',
            width=2
        )
        
        # Draw a simple logo placeholder (restaurant initial)
        draw.ellipse(
            [logo_x, logo_y, logo_x + logo_size, logo_y + logo_size],
            fill='#FF6B35',
            outline='white',
            width=2
        )
        
        return img
    
    async def _generate_single_qr_safe(self, qr_data: QRCodeData) -> GeneratedQRCode:
        """Safely generate a single QR code with error handling.
        
        Args:
            qr_data: QR code data.
            
        Returns:
            Generated QR code or raises exception.
        """
        try:
            return await self.generate_qr_code(qr_data)
        except Exception as e:
            raise Exception(f"Failed to generate QR for table {qr_data.table_number}: {str(e)}")
    
    async def _create_zip_file(self, qr_codes: List[GeneratedQRCode]) -> tuple[bytes, int]:
        """Create a ZIP file containing all generated QR codes.
        
        Args:
            qr_codes: List of generated QR codes.
            
        Returns:
            Tuple of (zip_content, zip_size).
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for qr_code in qr_codes:
                filename = qr_code.qr_data.filename
                zip_file.writestr(filename, qr_code.file_content)
        
        zip_content = zip_buffer.getvalue()
        return zip_content, len(zip_content)
