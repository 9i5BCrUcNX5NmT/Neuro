import pandas as pd
import numpy as np

class Auction:
    price = {"high" : 0, "mid" : 5, "low" : 10}
    
    def __init__(self):
        df_sell = pd.DataFrame(columns=["lot_id", "bet", "how"])
        df_buy = pd.DataFrame(columns=["user_id", "bet", "how"])

        df_sell.set_index("lot_id", inplace=True)
        df_buy.set_index("user_id", inplace=True)

        self.df_sell, self.df_buy = df_sell, df_buy
    
    def add_bet_sell(self, who, lot):
        self.df_sell.loc[who] = [self.price[who], lot]
    
    def add_bet_buy(self, who, bet, how):
        self.df_buy.loc[who] = [bet, how]
    
    def __loop_sort_table(self, ind, s_df_buy, s_df_sell):
        df_buy = s_df_buy.copy().drop(ind)
        df_sell = s_df_sell.copy()
        damage = 0

        while len(df_buy) > 0 and len(df_sell) > 0:
            how_buy, how_sell = df_buy["how"][0], df_sell["how"][0]
            pr = max(df_sell["bet"][0], df_buy["bet"][0])

            if how_sell <= how_buy:
                df_sell.drop(df_sell.index[0], inplace=True)
                df_buy["how"][0] -= how_sell
                damage += how_sell * pr
            else:
                df_buy.drop(df_buy.index[0], inplace=True)
                df_sell["how"][0] -= how_buy
                damage += how_buy * pr

            df_sell.drop(df_sell[df_sell["how"] == 0].index, inplace=True)
            df_buy.drop(df_buy[df_buy["how"] == 0].index, inplace=True)

        df_buy = s_df_buy.copy()
        df_sell = s_df_sell.copy()
        heal = 0

        while len(df_buy) > 0 and len(df_sell) > 0:
            how_buy, how_sell = df_buy["how"][0], df_sell["how"][0]
            pr = max(df_sell["bet"][0], df_buy["bet"][0])

            if how_sell <= how_buy:
                df_sell.drop(df_sell.index[0], inplace=True)
                df_buy["how"][0] -= how_sell
                heal += how_sell * pr
            else:
                df_buy.drop(df_buy.index[0], inplace=True)
                df_sell["how"][0] -= how_buy
                heal += how_buy * pr

            df_sell.drop(df_sell[df_sell["how"] == 0].index, inplace=True)
            df_buy.drop(df_buy[df_buy["how"] == 0].index, inplace=True)

        return damage - heal

    def __sort_table(self):
        sort_table = pd.DataFrame(columns=["user_id", "how", "total"])
        sort_table.set_index("user_id", inplace=True)

        df_buy = self.df_buy.copy()
        df_sell = self.df_sell.copy()

        while len(df_buy) > 0 and len(df_sell) > 0:
            how_buy, how_sell = df_buy["how"][0], df_sell["how"][0]
            if how_sell <= how_buy:
                try:
                    sort_table.loc[df_buy.index[0]] += [how_sell, self.__loop_sort_table(df_buy.index[0], df_buy, df_sell)]
                except KeyError:
                    sort_table.loc[df_buy.index[0]] = [how_sell, self.__loop_sort_table(df_buy.index[0], df_buy, df_sell)]

                df_sell.drop(df_sell.index[0], inplace=True)
                df_buy["how"][0] -= how_sell
            else:
                try:
                    sort_table.loc[df_buy.index[0]] += [how_buy, self.__loop_sort_table(df_buy.index[0], df_buy, df_sell)]
                except KeyError:
                    sort_table.loc[df_buy.index[0]] = [how_buy, self.__loop_sort_table(df_buy.index[0], df_buy, df_sell)]

                df_buy.drop(df_buy.index[0], inplace=True)
                df_sell["how"][0] -= how_buy

            df_sell.drop(df_sell[df_sell["how"] == 0].index, inplace=True)
            df_buy.drop(df_buy[df_buy["how"] == 0].index, inplace=True)
        return sort_table

    def __loop(self):
        self.df_sell.sort_values(by="bet", inplace=True)
        self.df_buy.sort_values(by=["bet", "how"], ascending=False, inplace=True)

        columns=["user_id", "how", "price", "seller"]
        log_for_loop = pd.DataFrame(columns=columns)

        while len(self.df_buy) > 0 and len(self.df_sell) > 0:
            how_buy, how_sell = self.df_buy["how"][0], self.df_sell["how"][0]
            pr = max(self.df_sell["bet"][0], self.df_buy["bet"][0])

            if how_sell <= how_buy:
                bad_print = pd.DataFrame([[self.df_buy.index[0], how_sell, pr * how_sell, self.df_sell.index[0]]], columns=columns)
                log_for_loop = pd.concat((log_for_loop, bad_print), ignore_index=True)
                
                self.df_sell.drop(self.df_sell.index[0], inplace=True)
                self.df_buy["how"][0] -= how_sell
            else:
                bad_print = pd.DataFrame([[self.df_buy.index[0], how_buy, pr * how_buy, self.df_sell.index[0]]], columns=columns)
                log_for_loop = pd.concat((log_for_loop, bad_print), ignore_index=True)

                self.df_buy.drop(self.df_buy.index[0], inplace=True)
                self.df_sell["how"][0] -= how_buy

            self.df_sell.drop(self.df_sell[self.df_sell["how"] == 0].index, inplace=True)
            self.df_buy.drop(self.df_buy[self.df_buy["how"] == 0].index, inplace=True)
            
        self.log_for_loop = log_for_loop
        
    def __nice_print(self):
        print("Контракты", self.log_for_loop, "Остались",\
            pd.concat([self.df_buy, self.df_sell], keys=["Покупатели", "Продавцы"]), sep="\n-----\n")

    def multi(self):
        self.__loop()
        self.__nice_print()
        self.__init__()

    def VCG(self):
        sort_table = self.__sort_table().sort_values(by=["how"], ascending=False)
        sort_table.sort_values(by=["total"], inplace=True)
        self.df_buy = self.df_buy.loc[sort_table.index]
        self.multi()

if __name__ != "__main__":
    print("Пример аукциона VCG\n")
    a = Auction()
    for i in "high mid low".split():
        a.add_bet_sell(i, np.random.randint(1, 100))
    for i in "one two three four five six seven eight nine ten".split():
        a.add_bet_buy(i, np.random.randint(1, 10), np.random.randint(1, 25))
    print(pd.concat([a.df_buy.copy(), a.df_sell.copy()], keys=["Покупатели", "Продавцы", "Энергия"]), end="\n-----\n")
    print(pd.DataFrame([a.df_buy["how"].sum(), a.df_sell["how"].sum()], index=["Хотят", "Есть"], columns=["Энергия"]), end="\n-----\n")
    a.VCG()