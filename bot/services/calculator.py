from typing import Dict, Any

class FeeCalculator:
    @staticmethod
    def calculate(amount: float, method: str) -> Dict[str, Any]:
        """
        Calculate fees based on method.
        Matches logic from Calculator.jsx
        
        Algorithm:
        1. Exchange Fee (Method specific %)
        2. Internal Fee % (7%)
        3. Internal Fee Fixed ($5)
        4. P2P Fee (3%)
        """
        if amount <= 0:
            return None
            
        fees = {
            "pay_paypal": 6.0,
            "stripe_card": 7.0, # Default for Stripe
            "stripe_apple": 7.0,
            "stripe_google": 7.0,
            "stripe_link": 7.0,
            "pay_crypto": 0.0, # Assuming 0 for now as not specified in JS, but usually crypto has network fees. Using 0 to match visual assumption or explicit defaults.
            # Actually JS had: PayPal 6%, Bank 8.5%, Stripe 7%.
        }
        
        # Mappings from callback data to fee percentage
        # Simplified mapping based on JS
        method_fee_percent = 0.0
        if "paypal" in method:
            method_fee_percent = 6.0
        elif "bank" in method: # Not in python buttons yet but good to have
            method_fee_percent = 8.5
        elif "stripe" in method:
            method_fee_percent = 7.0
        
        # 1. Exchange Fee
        exchange_fee = (amount * method_fee_percent) / 100
        after_exchange = amount - exchange_fee
        
        # 2. Internal Fee % (7%)
        internal_percent_fee = (amount * 7.0) / 100
        after_internal_percent = after_exchange - internal_percent_fee
        
        # 3. Fixed Internal Fee ($5)
        internal_fixed_fee = 5.0
        after_internal_fixed = after_internal_percent - internal_fixed_fee
        
        # 4. P2P Fee (3%)
        p2p_fee = (after_internal_fixed * 3.0) / 100
        before_rounding = after_internal_fixed - p2p_fee
        
        # Rounding strategy: No rounding (User request)
        # However, we must ensure it's not negative
        total_payout = before_rounding
        if total_payout < 0:
            total_payout = 0.0
            
        return {
            "input_amount": amount,
            "method_fee_percent": method_fee_percent,
            "exchange_fee": exchange_fee,
            "service_fee": internal_percent_fee + internal_fixed_fee,
            "p2p_fee": p2p_fee,
            "total_payout": total_payout
        }
