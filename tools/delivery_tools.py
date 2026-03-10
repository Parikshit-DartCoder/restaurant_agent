from utils.arabic_text import canonicalize_district

DISTRICTS = {
    "النرجس": {"delivery_fee": 15, "time": "35 دقيقة"},
    "العقيق": {"delivery_fee": 12, "time": "30 دقيقة"},
    "الملقا": {"delivery_fee": 10, "time": "25 دقيقة"},
}


def check_delivery_district(district):
    canonical = canonicalize_district(district)

    if canonical and canonical in DISTRICTS:
        d = DISTRICTS[canonical]
        return {
            "covered": True,
            "district": canonical,
            "delivery_fee": d["delivery_fee"],
            "estimated_time": d["time"],
        }

    return {
        "covered": False,
        "district": canonical,
        "delivery_fee": 0,
        "estimated_time": None,
    }