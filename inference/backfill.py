import datetime
from main import get_mysql_connection, handle_s3_event

MYSQL_CONN = None


def create_s3_event(date_string: str, news_source: str, bucket_name: str) -> dict:
    return (
        {
            "Records": [
                {
                    "s3": {
                        "bucket": {
                            "name": f"{bucket_name}"
                        },
                        "object": {
                            "key": f"{date_string}/{news_source}.json"
                        }
                    }
                }
            ]
        })


if __name__ == "__main__":
    DAYS_TO_BACKILL = 17

    news_sources = ["fox", "cnn", "nytimes"]
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(17)]
    dates_complete = []

    if MYSQL_CONN is None:
        MYSQL_CONN = get_mysql_connection()

    for date in date_list:
        # delete existing records for that date in MySQL
        date_str_mysql = date.strftime("%Y-%m-%d")
        with MYSQL_CONN.begin() as conn:
            delete_query = f"DELETE FROM news WHERE date = '{date_str_mysql}'"
            print(delete_query)
            conn.execute(delete_query)
        # iter over sources and backfill for that date
        for source in news_sources:
            date_str_s3 = date.strftime("%Y/%m/%d")
            event = create_s3_event(date_str_s3, source, "news-you-choose")
            print(event)
            # trigger the main lambda function
            handle_s3_event(event, None)
        dates_complete.append(date_str_mysql)

    print(f"Done for dates: {tuple(dates_complete)}")
