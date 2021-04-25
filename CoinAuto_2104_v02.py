import time
import datetime
import requests
import pybithumb
from slacker import Slacker

# 빗썸, 변동성돌파전략, slacker 메제지 확인 필요


slack = Slacker('xoxb-1623925257904-1623926509472-dJNktrWydtIsuVpnnKReT74V')
def dbgout(message):
    """인자로 받은 문자열을 파이썬 셸과 슬랙으로 동시에 출력한다."""
    print(datetime.datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    slack.chat.post_message('#stock', strbuf)

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pybithumb.get_ohlcv(ticker)
    df = df.tail(2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    t_now = datetime.datetime.now()
    start_time = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pybithumb.get_ohlcv(ticker)
    df = df.tail(15)
    ma15 = df['close'].rolling(15).mean().iloc[-1] # rolling(i) : i 갯수의 평균값 평균값
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balance = bithumb.get_balance(ticker)[2]  # 받은 값 = (보유코인량, 매도 주문 코인량, 원화보유량, 매수거래 원화량)
    return balance


def get_current_price(ticker):
    """현재가 조회"""
    current_price = int(pybithumb.get_current_price(ticker))
    return current_price


# 로그인
api_key = "4c56e40d778edebd9652dedb50bf22c6"
secret_key = "7de1c5f20b7a8ad60755741587b8ec56"
bithumb = pybithumb.Bithumb(api_key, secret_key)
print("autotrade start")
# 시작 메세지 슬랙 전송
# dbgout("autotrade start")

ticker = "BTC"
k = 0.5

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(ticker)
        end_time = start_time + datetime.timedelta(days=1)
        print(now)

        if start_time < now < (end_time - datetime.timedelta(seconds=10)):
            target_price = get_target_price(ticker, k)
            print(target_price)
            ma15 = get_ma15(ticker)
            current_price = get_current_price(ticker)
            print(current_price)
            print(get_balance(ticker))
            if target_price < current_price : # and ma15 < current_price : 상승장일때는 이것 추가도 좋음.
                krw = get_balance(ticker)
                buy_money = krw * 0.5
                if krw > 5000:
                    buy_coins = buy_money / current_price  # 잔고의 50% 구매
                    split_point = str(round(buy_coins, 12)).split(".")
                    for i in range(len(split_point)):
                        if i == 0:  # 1보다 큰 정수 부분
                            buy_coins = float(split_point[i])
                    else:  # 1보다 작은 실수 부분
                        buy_coins = buy_coins + float("0" + "." + split_point[i][:4])
                    order_result = bithumb.buy_market_order(ticker, buy_coins)  # 시장가 매수
                    # dbgout("BTC buy price : " + current_price)
                    # dbgout("BTC buy coin unit : " + buy_coins)
                    print("BTC buy price : " + current_price)
                    print("BTC buy coin unit : " + buy_coins)
        else:
            sell_coins = bithumb.get_balance(ticker)[0]
            current_price = get_current_price(ticker)
            if (sell_coins*current_price) < 5000:
                # dbgout("closed sell is none")
                print("closed sell is none")
                pass

            else:
                if sell_coins<0.0001: # 비트코인 주문 최소한도 미만이라서 중단
                    # dbgout("closed sell is none")
                    print("closed sell is none")
                else: # 주문수량의 소수점 5자리 미만 숫자를 버립니다.
                    split_point=str(round(sell_coins,12)).split(".")
                    for i in range(len(split_point)):
                        if i==0: # 1보다 큰 정수 부분
                            sell_coins=float(split_point[i])
                        else: # 1보다 작은 실수 부분
                            sell_coins=sell_coins+float("0"+"."+split_point[i][:4])
                    order_result = bithumb.sell_market_order(ticker, sell_coins)
                    # dbgout("BTC sell price : " + current_price)
                    # dbgout("BTC sell coin unit : " + sell_coins)
                    print("BTC sell price : " + current_price)
                    print("BTC sell coin unit : " + sell_coins)
        time.sleep(1800)  # 30분마다 확인해서 구매여부 판단.
    except Exception as e:
        print(e)
        time.sleep(10)