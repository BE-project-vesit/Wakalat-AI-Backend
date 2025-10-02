"""
Limitation Checker Tool
Checks limitation periods for filing cases under Indian law
"""
import json
from datetime import datetime, timedelta
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# Limitation periods as per Limitation Act, 1963
LIMITATION_PERIODS = {
    "suit_for_possession_of_immovable_property": {"years": 12, "article": "65"},
    "suit_for_money_lent": {"years": 3, "article": "54"},
    "suit_on_contract": {"years": 3, "article": "113"},
    "suit_for_compensation_tort": {"years": 3, "article": "113"},
    "suit_for_specific_performance": {"years": 3, "article": "54"},
    "suit_for_recovery_of_wages": {"years": 3, "article": "113"},
    "appeal_to_high_court": {"days": 90, "article": "116"},
    "appeal_to_supreme_court": {"days": 90, "article": "116"},
    "application_for_review": {"days": 30, "article": "121"},
    "suit_for_cancellation_of_instrument": {"years": 3, "article": "59"},
    "suit_under_negotiable_instruments_act": {"years": 3, "article": "56"},
    "defamation_suit": {"years": 1, "article": "74"},
    "motor_accident_claim": {"years": 2, "article": "Motor Vehicles Act"},
    "consumer_complaint": {"years": 2, "article": "Consumer Protection Act"}
}


async def check_limitation_period(
    case_type: str,
    cause_of_action_date: str,
    special_circumstances: Optional[str] = None
) -> str:
    """
    Check limitation period for a case
    
    Args:
        case_type: Type of case or cause of action
        cause_of_action_date: Date when cause of action arose (YYYY-MM-DD)
        special_circumstances: Special circumstances affecting limitation
    
    Returns:
        JSON string with limitation analysis
    """
    logger.info(f"Checking limitation for case type: {case_type}")
    
    try:
        # Parse the cause of action date
        try:
            coa_date = datetime.strptime(cause_of_action_date, "%Y-%m-%d")
        except ValueError:
            return json.dumps({
                "error": "Invalid date format. Use YYYY-MM-DD"
            }, indent=2)
        
        current_date = datetime.now()
        time_elapsed = current_date - coa_date
        
        # Find matching limitation period
        limitation_info = None
        matched_type = None
        
        # Try exact match first
        if case_type.lower().replace(" ", "_") in LIMITATION_PERIODS:
            matched_type = case_type.lower().replace(" ", "_")
            limitation_info = LIMITATION_PERIODS[matched_type]
        else:
            # Try partial match
            for key in LIMITATION_PERIODS:
                if case_type.lower() in key or key in case_type.lower():
                    matched_type = key
                    limitation_info = LIMITATION_PERIODS[key]
                    break
        
        if not limitation_info:
            # Default to 3 years for suits and 90 days for appeals
            if "appeal" in case_type.lower():
                limitation_info = {"days": 90, "article": "116"}
                matched_type = "appeal (default)"
            else:
                limitation_info = {"years": 3, "article": "113"}
                matched_type = "suit (default)"
        
        # Calculate limitation period
        if "years" in limitation_info:
            limitation_end = coa_date + timedelta(days=365 * limitation_info["years"])
            period_str = f"{limitation_info['years']} years"
        elif "days" in limitation_info:
            limitation_end = coa_date + timedelta(days=limitation_info["days"])
            period_str = f"{limitation_info['days']} days"
        else:
            limitation_end = coa_date + timedelta(days=365 * 3)
            period_str = "3 years (default)"
        
        days_remaining = (limitation_end - current_date).days
        is_within_limitation = days_remaining > 0
        
        result = {
            "case_type": case_type,
            "matched_category": matched_type,
            "cause_of_action_date": cause_of_action_date,
            "current_date": current_date.strftime("%Y-%m-%d"),
            "limitation_period": period_str,
            "article_reference": limitation_info["article"],
            "limitation_expires_on": limitation_end.strftime("%Y-%m-%d"),
            "days_elapsed": time_elapsed.days,
            "days_remaining": days_remaining if is_within_limitation else 0,
            "is_within_limitation": is_within_limitation,
            "status": "Within limitation period" if is_within_limitation else "BARRED BY LIMITATION",
            "special_circumstances": special_circumstances,
            "notes": []
        }
        
        # Add notes based on special circumstances
        if special_circumstances:
            result["notes"].append(
                "Special circumstances may affect limitation. "
                "Consult Sections 4-24 of Limitation Act, 1963 for exclusions and extensions."
            )
        
        if not is_within_limitation:
            result["notes"].append(
                "Case appears to be time-barred. However, consider: "
                "1) Section 5 - Extension of prescribed period in certain cases, "
                "2) Section 6 - Legal disability, "
                "3) Section 17 - Effect of fraud or mistake, "
                "4) Section 18 - Effect of acknowledgment in writing"
            )
        
        if days_remaining <= 30 and is_within_limitation:
            result["notes"].append(
                "⚠️ URGENT: Less than 30 days remaining to file!"
            )
        
        result["disclaimer"] = (
            "This is an automated calculation. "
            "Always verify with the Limitation Act, 1963 and consult qualified legal counsel. "
            "Specific facts may attract different limitation periods."
        )
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        logger.error(f"Error checking limitation: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)
