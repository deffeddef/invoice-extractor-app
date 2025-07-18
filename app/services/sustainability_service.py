import os
from typing import Optional
from app.models.invoice import Invoice, LineItem, SustainabilityMetrics, Vendor
from functools import lru_cache

class SustainabilityService:
    def __init__(self):
        # Initialize any API clients here if needed
        pass

    def _query_ecovadis(self, vendor_name: str) -> Optional[str]:
        """
        Placeholder for querying EcoVadis API for a vendor's rating.
        In a real scenario, this would involve an HTTP request to the EcoVadis API.
        """
        print(f"Querying EcoVadis for {vendor_name}...")
        # Simulate API call
        if "GreenCorp" in vendor_name:
            return "Gold"
        return "Bronze"

    def _query_bcorp(self, vendor_name: str) -> Optional[bool]:
        """
        Placeholder for querying B-Corp status.
        """
        print(f"Querying B-Corp for {vendor_name}...")
        # Simulate API call
        return "EcoSolutions" in vendor_name

    def _query_eu_ecolabel(self, item_description: str) -> Optional[bool]:
        """
        Placeholder for querying EU Ecolabel status for an item.
        """
        print(f"Querying EU Ecolabel for {item_description}...")
        # Simulate API call
        return "recycled paper" in item_description.lower()

    def _query_co2_api(self, item_description: str, quantity: float) -> Optional[float]:
        """
        Placeholder for querying a CO2 emissions API for an item.
        Returns CO2 emissions in kgCO2e.
        """
        print(f"Querying CO2 API for {item_description} (x{quantity})...")
        # Simulate API call: higher CO2 for certain items
        if "electronics" in item_description.lower():
            return 50.0 * quantity # High CO2
        elif "transport" in item_description.lower():
            return 10.0 * quantity # Medium CO2
        return 1.0 * quantity # Low CO2

    def calculate_item_sustainability_score(self, item: LineItem) -> float:
        """
        Calculates a sustainability score for a single line item (0-100).
        This is a simplified calculation for demonstration.
        """
        score = 50.0 # Base score

        if self._query_eu_ecolabel(item.description):
            score += 20 # Boost for eco-labeled items
        
        co2_emissions = self._query_co2_api(item.description, item.quantity)
        if co2_emissions is not None:
            # Penalize for high CO2 emissions (example logic)
            if co2_emissions > 20.0:
                score -= 15
            elif co2_emissions > 5.0:
                score -= 5
            else:
                score += 10 # Reward for low CO2

        # Ensure score is within 0-100 bounds
        return max(0, min(100, score))

    def analyze_invoice_sustainability(self, invoice: Invoice) -> Invoice:
        """
        Analyzes the sustainability aspects of an entire invoice.
        Populates sustainability_metrics and updates line_items with scores.
        """
        print("Analyzing invoice for sustainability metrics...")
        updated_line_items = []
        co2_intensive_items_found = False
        total_co2_emissions = 0.0

        for item in invoice.line_items:
            item.sustainability_score = self.calculate_item_sustainability_score(item)
            
            # Check for CO2 intensive items
            co2_emissions = self._query_co2_api(item.description, item.quantity)
            if co2_emissions is not None and co2_emissions > 20.0: # Threshold for CO2 intensive
                co2_intensive_items_found = True
            if co2_emissions is not None: # Accumulate total CO2
                total_co2_emissions += co2_emissions

            updated_line_items.append(item)
        invoice.line_items = updated_line_items

        # Determine overall ESG risk and green vendor flag
        overall_esg_risk = "Medium"
        green_vendor_flag = False
        if invoice.vendor and invoice.vendor.name:
            ecovadis_rating = self._query_ecovadis(invoice.vendor.name)
            bcorp_status = self._query_bcorp(invoice.vendor.name)

            if ecovadis_rating == "Gold" or bcorp_status:
                green_vendor_flag = True
                overall_esg_risk = "Low"
            elif ecovadis_rating == "Silver":
                overall_esg_risk = "Medium-Low"

        invoice.sustainability_metrics = SustainabilityMetrics(
            overall_esg_risk=overall_esg_risk,
            green_vendor_flag=green_vendor_flag,
            co2_intensive_items_flag=co2_intensive_items_found,
            # packaging_waste_flag=packaging_waste_flag # Removed as not explicitly requested
        )
        print("Sustainability analysis complete.")
        return invoice

@lru_cache(maxsize=1)
def get_sustainability_service() -> SustainabilityService:
    """
    Factory function to create and cache a singleton instance of the SustainabilityService.
    """
    return SustainabilityService()
