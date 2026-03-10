DISTRICTS = {

    "النرجس": {"delivery_fee": 15, "time": "35 دقيقة"},
    "العقيق": {"delivery_fee": 12, "time": "30 دقيقة"},
    "الملقا": {"delivery_fee": 10, "time": "25 دقيقة"}
}

def check_delivery_district(district):

    if district in DISTRICTS:

        d = DISTRICTS[district]

        return {
            "covered": True,
            "delivery_fee": d["delivery_fee"],
            "estimated_time": d["time"]
        }

    return {
        "covered": False,
        "delivery_fee": 0,
        "estimated_time": None
    }