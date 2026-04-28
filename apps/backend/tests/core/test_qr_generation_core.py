#!/usr/bin/env python3
"""
Core QR generation functionality test.
Tests the QR generation service directly without API authentication.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.features.qr.infrastructure.qr_generation_service import QRGenerationService
from app.features.qr.domain.qr_entities import (
    QRCodeConfig,
    QRCodeData,
    QRFormat,
    QRSize,
    QRErrorCorrection,
)
from uuid import uuid4


async def test_qr_generation_core():
    """Test core QR generation functionality."""
    print("🚀 Testing Core QR Generation Functionality")
    print("=" * 60)

    # Initialize QR generation service
    qr_service = QRGenerationService()

    # Test data
    restaurant_id = uuid4()
    table_id = uuid4()
    restaurant_code = "TEST123"
    table_number = "T001"

    tests_passed = 0
    total_tests = 0

    # Test 1: Basic PNG QR Code Generation
    total_tests += 1
    print("\n📝 Test 1: Basic PNG QR Code Generation")
    try:
        qr_config = QRCodeConfig(
            format=QRFormat.PNG,
            size=QRSize.MEDIUM,
            error_correction=QRErrorCorrection.MEDIUM,
        )

        qr_data = QRCodeData(
            url=f"https://app.zergoqrf.com/menu/{restaurant_code}/{table_id}",
            table_id=table_id,
            restaurant_id=restaurant_id,
            restaurant_code=restaurant_code,
            table_number=table_number,
            config=qr_config,
        )

        generated_qr = await qr_service.generate_qr_code(qr_data)

        print(f"✅ PNG QR code generated successfully:")
        print(f"   - File size: {generated_qr.file_size} bytes")
        print(f"   - Format: {generated_qr.qr_data.config.format.value}")
        print(f"   - URL: {generated_qr.qr_data.url}")

        tests_passed += 1

    except Exception as e:
        print(f"❌ PNG QR generation failed: {str(e)}")

    # Test 2: SVG QR Code Generation
    total_tests += 1
    print("\n📝 Test 2: SVG QR Code Generation")
    try:
        qr_config = QRCodeConfig(
            format=QRFormat.SVG,
            size=QRSize.LARGE,
            error_correction=QRErrorCorrection.HIGH,
        )

        qr_data = QRCodeData(
            url=f"https://app.zergoqrf.com/menu/{restaurant_code}/{table_id}",
            table_id=table_id,
            restaurant_id=restaurant_id,
            restaurant_code=restaurant_code,
            table_number=table_number,
            config=qr_config,
        )

        generated_qr = await qr_service.generate_qr_code(qr_data)

        print(f"✅ SVG QR code generated successfully:")
        print(f"   - File size: {generated_qr.file_size} bytes")
        print(f"   - Format: {generated_qr.qr_data.config.format.value}")

        tests_passed += 1

    except Exception as e:
        print(f"❌ SVG QR generation failed: {str(e)}")

    # Test 3: QR Code Preview
    total_tests += 1
    print("\n📝 Test 3: QR Code Preview Generation")
    try:
        qr_config = QRCodeConfig(
            format=QRFormat.PNG,
            size=QRSize.SMALL,
            error_correction=QRErrorCorrection.MEDIUM,
        )

        qr_data = QRCodeData(
            url=f"https://app.zergoqrf.com/menu/{restaurant_code}/{table_id}",
            table_id=table_id,
            restaurant_id=restaurant_id,
            restaurant_code=restaurant_code,
            table_number=table_number,
            config=qr_config,
        )

        preview = await qr_service.generate_qr_preview(qr_data)

        print(f"✅ QR code preview generated successfully:")
        print(f"   - Preview URL length: {len(preview.preview_url)} chars")
        print(f"   - Preview content size: {len(preview.preview_content)} bytes")

        tests_passed += 1

    except Exception as e:
        print(f"❌ QR preview generation failed: {str(e)}")

    # Test 4: QR Code Validation
    total_tests += 1
    print("\n📝 Test 4: QR Code Validation")
    try:
        qr_config = QRCodeConfig(
            format=QRFormat.PNG,
            size=QRSize.MEDIUM,
            error_correction=QRErrorCorrection.MEDIUM,
        )

        qr_data = QRCodeData(
            url=f"https://app.zergoqrf.com/menu/{restaurant_code}/{table_id}",
            table_id=table_id,
            restaurant_id=restaurant_id,
            restaurant_code=restaurant_code,
            table_number=table_number,
            config=qr_config,
        )

        generated_qr = await qr_service.generate_qr_code(qr_data)
        is_valid = await qr_service.validate_qr_scannability(generated_qr)

        print(f"✅ QR code validation completed:")
        print(f"   - Is scannable: {is_valid}")

        tests_passed += 1

    except Exception as e:
        print(f"❌ QR validation failed: {str(e)}")

    # Test 5: Different Error Correction Levels
    total_tests += 1
    print("\n📝 Test 5: Different Error Correction Levels")
    try:
        error_levels = [
            QRErrorCorrection.LOW,
            QRErrorCorrection.MEDIUM,
            QRErrorCorrection.QUARTILE,
            QRErrorCorrection.HIGH,
        ]

        for error_level in error_levels:
            qr_config = QRCodeConfig(
                format=QRFormat.PNG,
                size=QRSize.MEDIUM,
                error_correction=error_level,
            )

            qr_data = QRCodeData(
                url=f"https://app.zergoqrf.com/menu/{restaurant_code}/{table_id}",
                table_id=table_id,
                restaurant_id=restaurant_id,
                restaurant_code=restaurant_code,
                table_number=table_number,
                config=qr_config,
            )

            generated_qr = await qr_service.generate_qr_code(qr_data)
            print(f"   - {error_level.value}: {generated_qr.file_size} bytes")

        print("✅ All error correction levels tested successfully")
        tests_passed += 1

    except Exception as e:
        print(f"❌ Error correction level testing failed: {str(e)}")

    # Test 6: Different Sizes
    total_tests += 1
    print("\n📝 Test 6: Different QR Code Sizes")
    try:
        sizes = [QRSize.SMALL, QRSize.MEDIUM, QRSize.LARGE, QRSize.XLARGE]

        for size in sizes:
            qr_config = QRCodeConfig(
                format=QRFormat.PNG,
                size=size,
                error_correction=QRErrorCorrection.MEDIUM,
            )

            qr_data = QRCodeData(
                url=f"https://app.zergoqrf.com/menu/{restaurant_code}/{table_id}",
                table_id=table_id,
                restaurant_id=restaurant_id,
                restaurant_code=restaurant_code,
                table_number=table_number,
                config=qr_config,
            )

            generated_qr = await qr_service.generate_qr_code(qr_data)
            print(f"   - {size.value}: {generated_qr.file_size} bytes")

        print("✅ All QR code sizes tested successfully")
        tests_passed += 1

    except Exception as e:
        print(f"❌ QR code size testing failed: {str(e)}")

    # Summary
    print("\n" + "=" * 60)
    print(
        f"📊 Core QR Generation Test Results: {tests_passed}/{total_tests} tests passed"
    )

    if tests_passed == total_tests:
        print("🎉 All core QR generation tests passed!")
        return True
    else:
        print(f"❌ {total_tests - tests_passed} core tests failed")
        return False


main = test_qr_generation_core


if __name__ == "__main__":
    success = asyncio.run(test_qr_generation_core())
    sys.exit(0 if success else 1)
