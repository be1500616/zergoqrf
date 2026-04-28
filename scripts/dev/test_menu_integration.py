#!/usr/bin/env python3
"""
Menu Management Integration Test Script

This script tests the complete menu management workflow end-to-end,
including category creation, menu item management, versioning, and publishing.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class MenuIntegrationTest:
    """Integration test class for menu management functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the test with base URL."""
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.auth_token = None
        self.restaurant_id = None
        self.test_data = {}
        
    async def setup(self):
        """Set up test environment."""
        console.print("[bold blue]Setting up Menu Management Integration Test...[/bold blue]")
        
        # For this test, we'll use a mock auth token and restaurant ID
        # In a real scenario, these would come from the authentication flow
        self.auth_token = "test_token_123"
        self.restaurant_id = "test_restaurant_456"
        
        console.print(f"✅ Base URL: {self.base_url}")
        console.print(f"✅ Restaurant ID: {self.restaurant_id}")
        
    async def cleanup(self):
        """Clean up test environment."""
        await self.client.aclose()
        console.print("[green]✅ Test cleanup completed[/green]")
        
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }
        
    async def test_category_management(self) -> bool:
        """Test category creation, update, and management."""
        console.print("\n[bold yellow]Testing Category Management...[/bold yellow]")
        
        try:
            # Test 1: Create root categories
            categories_data = [
                {"name": "Appetizers", "description": "Start your meal right"},
                {"name": "Main Course", "description": "Hearty main dishes"},
                {"name": "Desserts", "description": "Sweet endings"},
                {"name": "Beverages", "description": "Refreshing drinks"}
            ]
            
            created_categories = []
            for cat_data in categories_data:
                response = await self.client.post(
                    f"{self.base_url}/menu/categories",
                    headers=self.get_headers(),
                    json=cat_data
                )
                
                if response.status_code == 201:
                    category = response.json()
                    created_categories.append(category)
                    console.print(f"✅ Created category: {category['name']}")
                else:
                    console.print(f"❌ Failed to create category: {cat_data['name']}")
                    return False
            
            self.test_data['categories'] = created_categories
            
            # Test 2: Create subcategories
            main_course_id = next(cat['id'] for cat in created_categories if cat['name'] == 'Main Course')
            subcategories_data = [
                {"name": "Pasta", "description": "Italian pasta dishes", "parent_category_id": main_course_id},
                {"name": "Pizza", "description": "Wood-fired pizzas", "parent_category_id": main_course_id}
            ]
            
            for subcat_data in subcategories_data:
                response = await self.client.post(
                    f"{self.base_url}/menu/categories",
                    headers=self.get_headers(),
                    json=subcat_data
                )
                
                if response.status_code == 201:
                    subcategory = response.json()
                    console.print(f"✅ Created subcategory: {subcategory['name']}")
                else:
                    console.print(f"❌ Failed to create subcategory: {subcat_data['name']}")
                    return False
            
            # Test 3: Get category hierarchy
            response = await self.client.get(
                f"{self.base_url}/menu/categories/hierarchy",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                hierarchy = response.json()
                console.print(f"✅ Retrieved category hierarchy: {len(hierarchy)} root categories")
            else:
                console.print("❌ Failed to retrieve category hierarchy")
                return False
                
            return True
            
        except Exception as e:
            console.print(f"❌ Category management test failed: {str(e)}")
            return False
            
    async def test_menu_item_management(self) -> bool:
        """Test menu item creation, update, and management."""
        console.print("\n[bold yellow]Testing Menu Item Management...[/bold yellow]")
        
        try:
            categories = self.test_data.get('categories', [])
            if not categories:
                console.print("❌ No categories available for testing")
                return False
            
            # Test 1: Create menu items
            appetizer_category = next(cat for cat in categories if cat['name'] == 'Appetizers')
            
            menu_items_data = [
                {
                    "category_id": appetizer_category['id'],
                    "name": "Caesar Salad",
                    "description": "Fresh romaine lettuce with parmesan and croutons",
                    "base_price": 12.99,
                    "status": "available",
                    "dietary_indicators": ["vegetarian"],
                    "preparation_time": 10,
                    "variants": [
                        {"name": "Small", "price_adjustment": -3.00},
                        {"name": "Large", "price_adjustment": 4.00}
                    ],
                    "modifier_groups": [
                        {
                            "name": "Protein Add-ons",
                            "modifier_type": "single_select",
                            "is_required": False,
                            "modifiers": [
                                {"name": "Grilled Chicken", "price": 5.00},
                                {"name": "Grilled Shrimp", "price": 7.00}
                            ]
                        }
                    ]
                },
                {
                    "category_id": appetizer_category['id'],
                    "name": "Bruschetta",
                    "description": "Toasted bread with fresh tomatoes and basil",
                    "base_price": 8.99,
                    "status": "available",
                    "dietary_indicators": ["vegetarian", "vegan"],
                    "preparation_time": 5
                }
            ]
            
            created_items = []
            for item_data in menu_items_data:
                response = await self.client.post(
                    f"{self.base_url}/menu/items",
                    headers=self.get_headers(),
                    json=item_data
                )
                
                if response.status_code == 201:
                    item = response.json()
                    created_items.append(item)
                    console.print(f"✅ Created menu item: {item['name']} - ₹{item['base_price']}")
                else:
                    console.print(f"❌ Failed to create menu item: {item_data['name']}")
                    return False
            
            self.test_data['menu_items'] = created_items
            
            # Test 2: Update menu item
            item_to_update = created_items[0]
            update_data = {
                "description": "Updated: Fresh romaine lettuce with parmesan, croutons, and house dressing",
                "base_price": 13.99
            }
            
            response = await self.client.put(
                f"{self.base_url}/menu/items/{item_to_update['id']}",
                headers=self.get_headers(),
                json=update_data
            )
            
            if response.status_code == 200:
                updated_item = response.json()
                console.print(f"✅ Updated menu item: {updated_item['name']} - ₹{updated_item['base_price']}")
            else:
                console.print("❌ Failed to update menu item")
                return False
            
            # Test 3: Search menu items
            search_data = {
                "query": "salad",
                "category_id": appetizer_category['id']
            }
            
            response = await self.client.post(
                f"{self.base_url}/menu/items/search",
                headers=self.get_headers(),
                json=search_data
            )
            
            if response.status_code == 200:
                search_results = response.json()
                console.print(f"✅ Search found {len(search_results)} items")
            else:
                console.print("❌ Failed to search menu items")
                return False
                
            return True
            
        except Exception as e:
            console.print(f"❌ Menu item management test failed: {str(e)}")
            return False
            
    async def test_menu_versioning(self) -> bool:
        """Test menu versioning and publishing."""
        console.print("\n[bold yellow]Testing Menu Versioning & Publishing...[/bold yellow]")
        
        try:
            # Test 1: Create menu version
            version_data = {
                "version_name": "Summer Menu 2024",
                "description": "Fresh summer offerings with seasonal ingredients"
            }
            
            response = await self.client.post(
                f"{self.base_url}/menu/versions",
                headers=self.get_headers(),
                json=version_data
            )
            
            if response.status_code == 201:
                version = response.json()
                console.print(f"✅ Created menu version: {version['version_name']}")
                self.test_data['version'] = version
            else:
                console.print("❌ Failed to create menu version")
                return False
            
            # Test 2: Get menu versions
            response = await self.client.get(
                f"{self.base_url}/menu/versions",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                versions = response.json()
                console.print(f"✅ Retrieved {len(versions)} menu versions")
            else:
                console.print("❌ Failed to retrieve menu versions")
                return False
            
            # Test 3: Publish menu version
            publish_data = {
                "publish_immediately": True,
                "publish_notes": "Initial menu launch"
            }
            
            response = await self.client.post(
                f"{self.base_url}/menu/versions/{version['id']}/publish",
                headers=self.get_headers(),
                json=publish_data
            )
            
            if response.status_code == 200:
                published_version = response.json()
                console.print(f"✅ Published menu version: {published_version['version_name']}")
            else:
                console.print("❌ Failed to publish menu version")
                return False
            
            # Test 4: Get current live version
            response = await self.client.get(
                f"{self.base_url}/menu/versions/current",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                current_version = response.json()
                console.print(f"✅ Current live version: {current_version['version_name']}")
            else:
                console.print("❌ Failed to get current live version")
                return False
                
            return True
            
        except Exception as e:
            console.print(f"❌ Menu versioning test failed: {str(e)}")
            return False
            
    async def test_menu_structure_and_analytics(self) -> bool:
        """Test menu structure retrieval and analytics."""
        console.print("\n[bold yellow]Testing Menu Structure & Analytics...[/bold yellow]")
        
        try:
            # Test 1: Get menu structure
            response = await self.client.get(
                f"{self.base_url}/menu/structure",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                structure = response.json()
                categories_count = len(structure.get('categories', []))
                items_count = len(structure.get('items', []))
                console.print(f"✅ Menu structure: {categories_count} categories, {items_count} items")
            else:
                console.print("❌ Failed to retrieve menu structure")
                return False
            
            # Test 2: Get menu analytics
            response = await self.client.get(
                f"{self.base_url}/menu/analytics",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                analytics = response.json()
                console.print(f"✅ Menu analytics: {analytics.get('total_items', 0)} total items")
                console.print(f"   Average price: ₹{analytics.get('average_price', 0):.2f}")
            else:
                console.print("❌ Failed to retrieve menu analytics")
                return False
                
            return True
            
        except Exception as e:
            console.print(f"❌ Menu structure and analytics test failed: {str(e)}")
            return False
            
    async def run_all_tests(self) -> bool:
        """Run all integration tests."""
        console.print(Panel.fit(
            "[bold green]Menu Management Integration Test Suite[/bold green]\n"
            "Testing complete menu management workflow...",
            border_style="green"
        ))
        
        test_results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            # Run tests
            task = progress.add_task("Running tests...", total=None)
            
            test_results.append(("Category Management", await self.test_category_management()))
            test_results.append(("Menu Item Management", await self.test_menu_item_management()))
            test_results.append(("Menu Versioning", await self.test_menu_versioning()))
            test_results.append(("Structure & Analytics", await self.test_menu_structure_and_analytics()))
        
        # Display results
        console.print("\n[bold blue]Test Results Summary:[/bold blue]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Test Category", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Result", justify="center")
        
        all_passed = True
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            result_style = "green" if result else "red"
            table.add_row(test_name, status, f"[{result_style}]{'SUCCESS' if result else 'FAILED'}[/{result_style}]")
            if not result:
                all_passed = False
        
        console.print(table)
        
        # Final result
        if all_passed:
            console.print(Panel.fit(
                "[bold green]🎉 ALL TESTS PASSED! 🎉[/bold green]\n"
                "Menu management system is working correctly.",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[bold red]❌ SOME TESTS FAILED[/bold red]\n"
                "Please check the test output above for details.",
                border_style="red"
            ))
        
        return all_passed


async def main():
    """Main test execution function."""
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Initialize and run tests
    test_suite = MenuIntegrationTest(base_url)
    
    try:
        await test_suite.setup()
        success = await test_suite.run_all_tests()
        await test_suite.cleanup()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        await test_suite.cleanup()
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Test suite failed with error: {str(e)}[/red]")
        await test_suite.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
