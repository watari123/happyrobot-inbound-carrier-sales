from app.models import Load

def negotiate_rate(
    load: Load,
    carrier_offer: float,
    round_number: int
):

    # Escalate after 3 rounds
    if round_number > 3:
        return {
            "decision": "escalate",
            "counter_offer": None,
            "message": (
                "We’ve reached the limit of automated pricing approvals. "
                "I’m transferring you to a sales representative now."
            ),
            "should_transfer": True
        }

    # Accept if within target
    if carrier_offer <= load.target_rate:
        return {
            "decision": "accept",
            "counter_offer": carrier_offer,
            "message": (
                f"We can make ${carrier_offer:.0f} work on this load. "
                "I’ll transfer you now to finalize the booking."
            ),
            "should_transfer": True
        }

    # Counter if within max approved range
    if carrier_offer <= load.max_rate:

        midpoint = round(
            (load.target_rate + carrier_offer) / 2,
            2
        )

        return {
            "decision": "counter",
            "counter_offer": midpoint,
            "message": (
                f"I may have a little flexibility here. "
                f"Could you do ${midpoint:.0f}?"
            ),
            "should_transfer": False
        }

    # Reject if too high
    return {
        "decision": "reject",
        "counter_offer": load.max_rate,
        "message": (
            f"That’s above the current approved range for this load. "
            f"The highest I can currently offer is ${load.max_rate:.0f}."
        ),
        "should_transfer": False
    }
