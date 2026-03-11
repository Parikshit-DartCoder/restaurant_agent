from utils.arabic_text import canonicalize_district

DISTRICTS = {
    "الملقا": {"delivery_fee": 10, "time": "25 دقيقة"},
    "malqa": {"delivery_fee": 10, "time": "25 دقيقة"},
    "العقيق": {"delivery_fee": 12, "time": "30 دقيقة"},
    "aqiq": {"delivery_fee": 12, "time": "30 دقيقة"},
    "النرجس": {"delivery_fee": 15, "time": "35 دقيقة"},
    "narjis": {"delivery_fee": 15, "time": "35 دقيقة"},
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