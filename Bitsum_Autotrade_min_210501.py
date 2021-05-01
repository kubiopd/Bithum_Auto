import pybithumb
import requests
import pandas as pd
import datetime  # 거래 이력 데이터프레임에서 timestamp(시간)을 계산하기 위한 모듈 추가
import numpy as np
import matplotlib.pyplot as plt
from slacker import Slacker
import time, calendar
import json
# from Bitsum_analysis_class import *


######## 계 좌 정 보 #############################
api_key = "4c56e40d778edebd9652dedb50bf22c6"
secret_key = "7de1c5f20b7a8ad60755741587b8ec56"
bithumb = pybithumb.Bithumb(api_key, secret_key)
##################################################

######## 변 수 모 음 ##############################
coin_list = ['BTC', 'XRP', 'ETH', 'BCH', 'EOS', 'TRX', 'LTC', 'ADA', 'LINK', 'XLM', 'BSV', 'MLK', 'ONT', 'STEEM']
# 4/30 선정(빗썸 선정 메이저 11+3개) : BTC(비트코인), XRP(리플), ETH(이더리움), BCH(비트코인 캐시), EOS(이오스), TRX(트론), LTC(라이트코인), ADA(에이다), LINK(체인링크), XLM(스텔라루멘), BSV(비트코인에스브이), MLK(밀크), ONT(온톨로지), STEEM(스팀)
# 4/22 선정(빗썸 선정 메이저 11) : BTC(비트코인), XRP(리플), ETH(이더리움), BCH(비트코인 캐시), EOS(이오스), TRX(트론), LTC(라이트코인), ADA(에이다), LINK(체인링크), XLM(스텔라루멘), BSV(비트코인에스브이)
# 4/11 선정 : BTC(비트코인), XRP(리플), ETH(이더리움), BTT(비트토렌토), MVC(마이벌스), LF(링크플로우), ENJ(엔진코인), XNO(제노토큰), BTG(비트코인 골드), ETC(이더리움 클래식)

#dictionary를 불러올때
tf = open("Coin_buying_price_Bitsum.json", "r")
coin_bought_price = json.load(tf)
print(coin_bought_price)

# coin_bought_price = { 'BTC': 64432000 , 'XRP':1656, 'ETH':3003000, 'BCH': 1020000 , 'EOS':7025, 'TRX':148, 'LTC':298900, 'ADA':1534, 'LINK':42640, 'XLM':597, 'BSV':318700}
# 4/22 일 가격으로 넣음.
candle_period = '1h'  # 기본값 : 24h {1m, 3m, 5m, 10m, 30m, 1h, 6h, 12h, 24h 사용 가능}
date_range = 90  # call_data의 자료 기간을 선정함. 기본 30일이하며, 최대 2600일정도 받아옴.
slack = Slacker('xoxb-1623925257904-1623926509472-dJNktrWydtIsuVpnnKReT74V')
###################################################

######## 함 수 정 의 ################################
def dbgout(message):
    """인자로 받은 문자열을 파이썬 셸과 슬랙으로 동시에 출력한다."""
    print(datetime.datetime.now().strftime('[%m/%d %H:%M:%S]'), message)
    strbuf = datetime.datetime.now().strftime('[%m/%d %H:%M:%S] ') + message
    slack.chat.post_message('#stock', strbuf)

def get_current_price(coin_name):
    """현재가 조회"""
    current_price = int(pybithumb.get_current_price(coin_name))
    return current_price

def get_balance(coin_name):
    """잔고 조회"""
    balance = bithumb.get_balance(coin_name)[2]  # 받은 값 = (보유코인량, 매도 주문 코인량, 원화보유량, 매수거래 원화량)
    return balance

def get_target_price(coin_name, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pybithumb.get_ohlcv(coin_name)
    df = df.tail(2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price



################## 메 인 프 로 그 램 ########################
#if __name__ == '__main__':
#    while True:
#        t_now = datetime.datetime.now()
#        t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
#        t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
#        t_sell = t_now.replace(hour=14, minute=45, second=0, microsecond=0)
#        t_exit = t_now.replace(hour=14, minute=50, second=0, microsecond=0)
#        if t_now.minute == 30 and 0 <= t_now.second <= 10:  # 매시간 30분마다 실행함.
#            print("30분입니다.")

#            time.sleep(5)


while True:
    try:
        for coin_name in coin_list :
            balance = bithumb.get_balance(coin_name)  # 받은 값 = (보유코인량, 매도 주문 코인량, 원화보유량, 매수거래 원화량)
            print(coin_name, ':', balance)
            current_price = int(pybithumb.get_current_price(coin_name))
            time.sleep(0.1)
            value = balance[0] * current_price
            if value > 5000 :  # 5천원이상에 대해서만 매도 실시
                if (current_price/coin_bought_price[coin_name]) > 1.1 or (current_price/coin_bought_price[coin_name]) < 0.95 :
                    # 수익률 10%이상이거나, -5%이하면 매도 실시
                    print("%s : 매도" % coin_name)
                    sell_coins=balance[0]-balance[1]
                    split_point = str(round(sell_coins, 12)).split(".")
                    for i in range(len(split_point)):
                        if i == 0:  # 1보다 큰 정수 부분
                            sell_coins = float(split_point[i])
                        else:  # 1보다 작은 실수 부분
                            sell_coins = sell_coins + float("0" + "." + split_point[i][:4])
                    order_result = bithumb.sell_market_order(coin_name, sell_coins)
                    print("%s current_sell_price : %s" % (coin_name, current_price))
                    print("%s current_bought_price : %s" % (coin_name, coin_bought_price[coin_name]))
                    ratio = (current_price/coin_bought_price[coin_name]-1) * 100 #수익률
                    print("%s : 수익율 %s %% 내고 팔았음." % (coin_name, ratio))

                    coin_bought_price[coin_name] = current_price
                    # dictionary를 저장할때
                    tf = open("Coin_buying_price_Bitsum.json", "w")
                    json.dump(coin_bought_price, tf)
                    tf.close()

                else :
                    print("%s current_price : %s" % (coin_name, current_price))
                    print("%s current_bought_price : %s" % (coin_name, coin_bought_price[coin_name]))
                    print("%s : 팔지 않고 보유" % coin_name)
            else :
                # class를 불러서 매수해야 하는지 확인해야함.
                k = 0.3  #변동성 돌파 구간 설정값
                target_price = get_target_price(coin_name, k)
                current_price = get_current_price(coin_name)
                print("%s current_price : %s" % (coin_name, current_price))
                print("%s balance : %s" % (coin_name, get_balance(coin_name)))
                if current_price > target_price :
                # and ma15 < current_price : 상승장일때는 이것 추가도 좋음.
                    balance = get_balance(coin_name)
                    buy_money = balance * 0.15  # 보유 금액의 15% 구매
                    if balance > 5000:
                        buy_coins = buy_money / current_price
                        split_point = str(round(buy_coins, 12)).split(".")
                        for i in range(len(split_point)):
                            if i == 0:  # 1보다 큰 정수 부분
                                buy_coins = float(split_point[i])
                        else:  # 1보다 작은 실수 부분
                            buy_coins = buy_coins + float("0" + "." + split_point[i][:4])
                        order_result = bithumb.buy_market_order(coin_name, buy_coins)  # 시장가 매수
                        coin_bought_price[coin_name] = current_price

                        # dictionary를 저장할때
                        tf = open("Coin_buying_price_Bitsum.json", "w")
                        json.dump(coin_bought_price, tf)
                        tf.close()

                        # dbgout("BTC buy price : " + current_price)
                        # dbgout("BTC buy coin unit : " + buy_coins)
                        print(" %s buy price : %s" % (coin_name, + current_price))
                        print(" %s buy coin unit : %s " % (coin_name, buy_coins))

                    ### 구매하고나서, 그 값을 저장하고, 그 값을 불러서 확인할 수 있는 방법 찾기
                    ### while문으로 묶는 방법 추가, 매 60분마다 실시하는 것 확인.
        t_now = datetime.datetime.now()
        print(t_now)
        time.sleep(300)  # 30분마다 확인해서 구매여부 판단.
    except Exception as e:
        print(e)
        time.sleep(10)




# import json
# my_dict = { 'Apple': 4, 'Banana': 2, 'Orange': 6, 'Grapes': 11}
# coin_bought_price = { 'BTC': 63936000 , 'XRP':1577, 'ETH':3145000, 'BCH': 1025000 , 'EOS':6905, 'TRX':142, 'LTC':297500, 'ADA':1497, 'LINK':41920, 'XLM':564, 'BSV':324700}
# 4/22 일 가격으로 넣음.
# dictionary를 저장할때
# tf = open("Coin_buying_price_Bitsum.json", "w")
# json.dump(coin_bought_price,tf)
# tf.close()
# dictionary를 불러올때
# tf = open("Coin_buying_price_Bitsum.json", "r")
# new_dict = json.load(tf)
# print(new_dict)

#    f = open("Balance_Bitsum.txt", 'a') # 'r':읽기모드 - 파일을 읽기만 할 때 사용, 'w':쓰기모드 - 파일에 내용을 쓸 때 사용, 'a':추가모드 - 파일의 마지막에 새로운 내용을 추가 시킬 때 사용
#    f.write(coin_name, balance)
#    f.close()

# order_result = bithumb.sell_market_order(coin_name, sell_unit) # 시장가 매도
# order_result = bithumb.buy_market_order(coin_name, buy_coins) # 시장가 매수

# order_result = bithumb.sell_limit_order(coin_name,price,sell_coins) # 지정가 매도
# order_result = bithumb.buy_limit_order(coin_name, price, buy_coins) # 지정가 매수

# balance = bithumb.get_balance(coin_name)  # 받은 값 = (보유코인량, 매도 주문 코인량, 원화보유량, 매수거래 원화량)
#
# print(balance)
#
# sell_coins=balance[0]-balance[1]  #매도 가능 수량
#
# current_price = int(pybithumb.get_current_price(coin_name))
#
# buy_coins=(balance[2]-balance[3])/current_price  #매수 가능 수량
#
# print(sell_coins)
# print(current_price)
# print(buy_coins)
#
# orderbook = pybithumb.get_orderbook(coin_name)
# binding_price = orderbook.get("bids")[0]["price"]
#
# print(orderbook)
# print(binding_price)
#
#
# def target_price(sign): # sign은 보조지표에서 반환받은 현재 포지션 (매도 또는 매수)
#     orderbook = pybithumb.get_orderbook(coin_name)
#     if sign == "매수":
#         target=orderbook.get("bids")[0]["price"] # 첫 번째 매수호가
#     elif sign == "매도":
#         target=orderbook.get("asks")[0]["price"] # 첫 번째 매도호가
#     else:
#         target=pybithumb.get_current_price(coin_name)
#     return target
#
# def sell_order(balance):
#     sell_coins=balance[0]-balance[1] # 선행된 매도 주문으로 거래중인 코인수를 빼줍니다.
#     price=target_price("매도") # 주문 가격
#     # ######################### 매도주문 수량 보정 #########################
#     if sell_coins*price<5000:
#         order_result==None
#         return order_result, 로그파일
#     else:
#         if sell_coins<0.0001: # 비트코인 주문 최소한도 미만이라서 중단
#             order_result==None
#             return order_result, 로그파일
#         else: # 주문수량의 소수점 5자리 미만 숫자를 버립니다.
#             split_point=str(round(sell_coins,12)).split(".")
#             for i in range(len(split_point)):
#                 if i==0: # 1보다 큰 정수 부분
#                     sell_coins=float(split_point[i])
#                 else: # 1보다 작은 실수 부분
#                     sell_coins=sell_coins+float("0"+"."+split_point[i][:4])
#
#     #######################################################################
#     ########################## 주문 가격 타입 보정 #########################
#     if price<1000:
#         price=float(price)
#     else:
#         price=int(price)
#     #######################################################################
#     order_result=bithumb.sell_limit_order(coin_name,price,sell_coins)
#
#     return order_result
#
#
# def buy_order(balance):
#     price=target_price("매수") # 주문 가격
#     buy_coins=(balance[2]-balance[3])/price # 선행된 매수 주문으로 거래중인 금액을 빼줍니다.
#     ######################### 매수주문 수량 보정 #########################
#     if (balance[2]-balance[3])/price<0.0001 or (balance[2]-balance[3])<5000 :
#       # 비트코인 최소주문수량 0.0001 또는 잔액이 5000원보다 작으면 함수를 중단합니다.
#         order_result==None
#         return order_result
#     else: # 주문수량의 소수점 5자리 미만 숫자를 버립니다.
#         split_point=str(round(buy_coins,12)).split(".")
#         for i in range(len(split_point)):
#             if i==0: # 1보다 큰 정수 부분
#                 buy_coins=float(split_point[i])
#             else: # 1보다 작은 실수 부분
#                 buy_coins=buy_coins+float("0"+"."+split_point[i][:4])
#     #######################################################################
#     ######################### 주문 가격 타입 보정 #########################
#     if price<1000:
#         price=float(price)
#     else:
#         price=int(price)
#     #######################################################################
#     order_result=bithumb.buy_limit_order(coin_name,price,buy_coins)
#     #
#     # if order_result==None:
#     #     pass
#     # elif order_result[0]=="bid":
#     #     df_temp=pd.DataFrame({"order_type":order_result[0], "coin_name":order_result[1], "order_no":order_result[2], "cash_type":order_result[3], 'price':price, 'order_units':buy_coins, 'remain':buy_coins, "result":"0000", "order_time":pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'), "finish_time":0}, index=[0]) # 초기값
#     #     df_history=pd.concat([df_history,df_temp],ignore_index=True)
#     #     df_history.to_excel("df_history.xlsx",index=False) # 로그 파일 저장
#     # return df_history,order_result
#
#
