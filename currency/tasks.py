# from celery import shared_task
from schedule import Scheduler
import threading
import time
from currency.models import Currency, Comparison, ComparisonDetails, DayValues, DayValuesLowHigh, News, NewsAsset, Paragraph
import requests
from django.utils import timezone
from datetime import datetime, timedelta, time as Time
import arabic_reshaper
from bidi.algorithm import get_display
import random
from googletrans import Translator

translator = Translator()

# @shared_task()
# def add(x, y):
#     # print(5+9)
#     return x + y

ar_curs_sympols = ['EGP', 'AED', 'IQD', 'BHD', 'QAR', 'OMR', 'KWD', 'JOD',
                   'LBP', 'LYD', 'DZD', 'MAD', 'SAR', 'YER', 'TRY', 'SDG', 'TND']

ar_curs = Currency.objects.filter(sympol__in=ar_curs_sympols)

other_curs_sympols = ["CAD", "CHF", "CNY", "EUR", "GBP", "JPY", 'USD', 'MYR',
                      'PKR', 'RUB', 'MYR', 'MXN', 'ISK', 'IDR', 'DKK', 'CZK', 'BRL', 'ARS']

other_curs = Currency.objects.filter(sympol__in=other_curs_sympols)


def new_exchange():
    rise_assets = NewsAsset.objects.filter(asset_type__asset_type='rise')
    fall_assets = NewsAsset.objects.filter(asset_type__asset_type='fall')
    stability_assets = NewsAsset.objects.filter(
        asset_type__asset_type='stability')

    bases_currencies = Currency.objects.filter(
        currency_type__base_currency=True)
    for cur in bases_currencies:
        try:
            request = requests.get(
                f'https://api.metalpriceapi.com/v1/latest?api_key=6d738f6d27f371d626809920ef29112f&base={cur.sympol}'
            )
            data = request.json()['rates']
        except Exception as e:
            print(str(e))
            continue
        comparison = Comparison.objects.create(
            base_currency=cur,
        )
        time = datetime.strptime(comparison.date.strftime(
            "%j/%m/%y %H:%M"), "%j/%m/%y %H:%M").time()
        for key in data:
            print(key)
            normal_currency_qs = Currency.objects.filter(sympol=key)
            if normal_currency_qs.exists():
                normal_currency = normal_currency_qs.first()
                if time >= normal_currency.open_time and time <= normal_currency.close_time:
                    comparison_details = ComparisonDetails.objects.create(
                        normal_currency=normal_currency,
                        bye_value=float(data[key]),
                        comparison=comparison,
                        open_price=True if time >= normal_currency.open_time and time < normal_currency.open_time.replace(
                            hour=(normal_currency.open_time.hour+1) % 24) else False,
                        close_price=True if time <= normal_currency.close_time and time > normal_currency.close_time.replace(
                            hour=(normal_currency.close_time.hour-1) % 24) else False,
                    )
                    day_values, created = DayValues.objects.get_or_create(
                        date=datetime.today(), base_currency=cur)
                    qs = DayValuesLowHigh.objects.filter(
                        day_values=day_values, normal_currency=normal_currency).order_by('-day_values__date')
                    if qs.exists():
                        day_values_low_high = qs.first()
                        day_values_low_high.high_value = comparison_details.bye_value if comparison_details.bye_value > day_values_low_high.high_value else day_values_low_high.high_value
                        day_values_low_high.low_value = comparison_details.bye_value if comparison_details.bye_value < day_values_low_high.low_value else day_values_low_high.low_value
                        day_values_low_high.save()
                    else:
                        DayValuesLowHigh.objects.create(
                            day_values=day_values,
                            normal_currency=normal_currency,
                            low_value=comparison_details.bye_value,
                            high_value=comparison_details.bye_value
                        )
                    lqs = ComparisonDetails.objects.filter(
                        comparison__base_currency=cur,
                        comparison__date__date=datetime.today()-timedelta(days=1),
                        normal_currency=normal_currency,
                        close_price=True
                    )
                    excute = False
                    if normal_currency in ar_curs:
                        if comparison_details.open_price or comparison_details.close_price:
                            excute = True
                    elif normal_currency in other_curs:
                        if comparison_details.oprn_price or comparison_details.close_price:
                            excute = True
                        elif datetime.now().time() > Time(16.15) and datetime.now().time() < Time(17.15):
                            excute = True
                    if excute and lqs.exists():
                        last_close = lqs.first().bye_value

                        assets = []
                        if round(float(data[key]), 2) > round(last_close, 2):
                            assets = rise_assets
                        elif round(float(data[key]), 2) < round(last_close, 2):
                            assets = fall_assets
                        else:
                            assets = stability_assets
                        cur_name_ar = translator.translate(
                            cur.name, dest='ar').text
                        country_name_ar = translator.translate(
                            normal_currency.country.name, dest='ar').text
                        date_ar = translator.translate(
                            comparison.date.strftime("%A %-d %B, %Y"), dest='ar').text
                        normal_cur_ar = translator.translate(
                            normal_currency.name, dest='ar').text

                        if cur.currency_type == 'Metals':
                            header = f"سعر ال{cur_name_ar} في {country_name_ar} اليوم {date_ar}"
                            sub_header = f"سعر ال{cur_name_ar} في اليوم {date_ar} مقابل ال{translator.translate(normal_currency.name, dest='ar')}"
                            pqs = Paragraph.objects.filter(currency=cur)

                            body1 = f"{random.choice(assets).asset} سعر ال{cur_name_ar} اليوم في {country_name_ar} خلال تعاملات {date_ar} في محال واسواق الذهب بالمقارنة باسعار الذهب امس {translator.translate(datetime.today().strftime('%A'), dest='ar').text} عند اغلاق التعاملات والتداولات"
                            news = News.objects.create(
                                header=header,
                                sub_header=sub_header,
                                base_currency=cur,
                                normal_currency=normal_currency,
                                date=comparison.date,
                                body1=body1
                            )
                            if pqs.exists():
                                news.paragraphs = pqs.first()
                                news.save()
                        else:
                            pqs = Paragraph.objects.filter(
                                currency=normal_currency)
                            header = f"سعر ال{cur_name_ar} في {country_name_ar} اليوم {date_ar}"
                            sub_header = f"سعر ال{cur_name_ar} في اليوم {date_ar} مقابل ال{translator.translate(normal_currency.name, dest='ar')}"
                            body1 = f"{random.choice(assets).asset} سعر ال{cur_name_ar} اليوم في {country_name_ar} خلال تعاملات {date_ar} في مستهل التعاملات في البنوك واسواق الصرافة في {country_name_ar}"
                            body2 = f"{random.choice(assets).asset} سعر ال{cur_name_ar} في {country_name_ar} عند {round(comparison_details.bye_value, 2)} {normal_cur_ar} بحسب السعر المعلن من البنك المركزي والبنوك المحلية خلال التعاملات الرسمية"
                            news = News.objects.create(
                                date=comparison.date,
                                base_currency=cur,
                                normal_currency=normal_currency,
                                header=header,
                                sub_header=sub_header,
                                body1=body1,
                                body2=body2,
                            )
                            if pqs.exists():
                                news.paragraphs = pqs.first()
                                news.save()
                print('\n dooooone \n')
    print('ALL DOOOOOOOOONE')


def run_continuously(self, interval=1):
    """Continuously run, while executing pending jobs at each elapsed
    time interval.
    @return cease_continuous_run: threading.Event which can be set to
    cease continuous run.
    Please note that it is *intended behavior that run_continuously()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you set a continuous run interval
    of one hour then your job won't be run 60 times at each interval but
    only once.
    """

    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every(10).seconds.do(new_exchange)
    scheduler.run_continuously()
