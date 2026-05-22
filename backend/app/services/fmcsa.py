def verify_carrier_by_mc(mc_number: str):
    """
    Mock FMCSA verification service.
    Later this can be replaced with the real FMCSA API.
    """

    mock_carriers = {
        "123456": {
            "legal_name": "Lone Star Freight LLC",
            "authority_status": "ACTIVE",
            "insurance_status": "VALID",
            "safety_rating": "SATISFACTORY",
        },
        "789101": {
            "legal_name": "Midwest Cold Chain Inc",
            "authority_status": "ACTIVE",
            "insurance_status": "VALID",
            "safety_rating": "SATISFACTORY",
        },
        "555555": {
            "legal_name": "Risky Road Logistics",
            "authority_status": "INACTIVE",
            "insurance_status": "EXPIRED",
            "safety_rating": "CONDITIONAL",
        },
    }

    carrier = mock_carriers.get(mc_number)

    if not carrier:
        return {
            "mc_number": mc_number,
            "is_eligible": False,
            "reason": "Carrier not found in verification database",
            "risk_level": "UNKNOWN",
        }

    is_eligible = (
        carrier["authority_status"] == "ACTIVE"
        and carrier["insurance_status"] == "VALID"
        and carrier["safety_rating"] in ["SATISFACTORY", "NONE"]
    )

    risk_level = "LOW" if is_eligible else "HIGH"

    return {
        "mc_number": mc_number,
        "legal_name": carrier["legal_name"],
        "authority_status": carrier["authority_status"],
        "insurance_status": carrier["insurance_status"],
        "safety_rating": carrier["safety_rating"],
        "is_eligible": is_eligible,
        "risk_level": risk_level,
        "reason": "Carrier is eligible" if is_eligible else "Carrier failed compliance checks",
    }
