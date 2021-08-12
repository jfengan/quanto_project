import bisect
import numpy as np
import math
from scipy.optimize import brentq, newton
from scipy.special import ndtr


class BlackScholes:
    TAG_CALL = 'call'
    TAG_PUT = 'put'
    TAG_MID_VOL = 'mid_vol'
    TAG_ASK_VOL = 'ask_vol'
    TAG_BID_VOL = 'bid_vol'
    TAG_BS_DELTA = 'bs_delta'
    TAG_EXP_IN_DAYS = 'exp_in_days'
    TAG_STRIKE = 'strike'
    TAG_FORWARD = 'forward'

    CONST_NORM = math.sqrt(2.0 * np.pi)

    def __init__(self, s, k, r, q, vol_pnt, t, payoff):
        self.s = s
        self.k = k
        self.r = r
        self.q = q
        self.vol = vol_pnt
        self.t = t
        self.payoff = payoff.lower()
        self.is_call = BlackScholes.is_call(self.payoff)

        self.sqrt_t = math.sqrt(self.t) if self.t >= 0 else np.nan
        self.exp_neg_q_t = np.e ** (-self.q * self.t)
        self.exp_neg_r_t = np.e ** (-self.r * self.t)
        self.d1 = self.__d1() if self.sqrt_t > 0 else np.nan
        self.d2 = self.d1 - self.sqrt_t * self.vol if self.sqrt_t > 0 else np.nan
        self.n_d1 = ndtr(self.d1) if self.sqrt_t > 0 else np.nan
        self.n_d2 = ndtr(self.d2) if self.sqrt_t > 0 else np.nan
        self.raw_price = self.__price()
        self.raw_delta = self.__delta()
        self.phi_d1 = BlackScholes.phi(self.d1) if self.sqrt_t > 0 else np.nan
        self.phi_d2 = BlackScholes.phi(self.d2) if self.sqrt_t > 0 else np.nan


    @classmethod
    def phi(cls, x):
        return np.e ** (-x * x / 2.0) / BlackScholes.CONST_NORM

    def __delta(self):
        if self.t == 0:
            if self.is_call:
                return 1.0 if self.s > self.k else 0.0
            else:
                return -1.0 if self.s < self.k else 0.0
        if self.is_call:
            return self.exp_neg_q_t * self.n_d1
        else:
            return -self.exp_neg_q_t * (1. - self.n_d1)

    @classmethod
    def cnorm(cls, x):
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    @classmethod
    def is_call(cls, option_type):
        return option_type == cls.TAG_CALL

    def __d1(self):
        return (math.log(self.s / self.k) +
                (self.r - self.q + self.vol * self.vol / 2.0) * self.t) / (self.vol * self.sqrt_t)

    def __d2(self):
        return (math.log(self.s / self.k) +
                (self.r - self.q - self.vol * self.vol / 2.0) * self.t) / (self.vol * self.sqrt_t)

    def __price(self):
        return self.call_price() if self.is_call else self.put_price()

    def price(self):
        return self.raw_price

    def dollar_delta(self):
        return self.raw_delta * self.s

    @classmethod
    def intrinsic(cls, is_call, s, k, exp_neg_q_t, exp_neg_r_t):
        sign = 1.0 if is_call else -1.0
        payout = sign * (exp_neg_q_t * s - exp_neg_r_t * k)
        return max(0.0, payout)

    def call_price(self):
        if self.t == 0:
            return BlackScholes.intrinsic(True, self.s, self.k, 1.0, 1.0)
        return self.s * self.exp_neg_q_t * self.n_d1 - self.exp_neg_r_t * self.k * self.n_d2

    def put_price(self):
        if self.t == 0:
            return BlackScholes.intrinsic(False, self.s, self.k, 1.0, 1.0)
        return self.exp_neg_r_t * self.k * (1.0 - self.n_d2) - self.s * self.exp_neg_q_t * (1.0 - self.n_d1)

    def delta(self):
        return self.raw_delta

    def __bump_spot(self, move):
        return BlackScholes(self.s * (1 + move), self.k, self.r, self.q, self.vol, self.t, self.payoff)

    def __bump_strike(self, move):
        return BlackScholes(self.s * (1 + move), self.k, self.r, self.q, self.vol, self.t, self.payoff)

    def gamma(self):
        if self.t == 0:
            return 0
        return self.exp_neg_q_t * self.phi_d1 / (self.s * self.vol * self.sqrt_t)

    def dollar_gamma(self):
        return self.gamma() * self.s ** 2


def get_iv(mkt_price, payoff, s, k, r, q, t, precision=1e-10, max_iter=100) -> float:
    lower_bdd = 1e-6
    upper_bdd = 1000

    def function(vol):
        return BlackScholes(s, k, r, q, vol, t, payoff).price() - mkt_price

    if function(lower_bdd) * function(upper_bdd) > 0:
        return np.nan
    else:
        solved_vol = brentq(function, lower_bdd, upper_bdd, xtol=precision, maxiter=max_iter)
    return solved_vol


def get_iv_newton_r(mkt_price, payoff, s, k, r, q, t, precision=1e-10, max_iter=100) -> float:

    def function(vol):
        return BlackScholes(s, k, r, q, vol, t, payoff).price() - mkt_price

    def bs_vega(vol):
        return s * np.sqrt(t) * ndtr((np.log(s/k) + (r - q + 0.5 * vol ** 2))/(vol * np.sqrt(t)))

    solved_vol = newton(function, 1, fprime=bs_vega, maxiter=500, rtol=1.e-10)
    return solved_vol


def get_forwad_price(call_price, put_price, strike, r, t):
    return call_price - put_price + strike * math.exp(-1 * r * t)


def get_iq(call_price, put_price, strike, r, t, spot):
    fwd_curr = (call_price - put_price) + np.exp(-r * t) * strike
    # print(f"forward price at {t}:  {fwd}")
    return -1 / t * math.log(fwd_curr / spot)


def get_iv_newton(mkt_price, payoff, s, k, r, q, t, precision=1e-10, max_iter=100):
    def function(vol):
        return BlackScholes(s, k, r, q, vol, t, payoff).price() - mkt_price

    i = 0
    dvol = 0.00001
    init_vol = 0.9
    while(i < 100):
        price1 = function(init_vol)
        price2 = function(init_vol-dvol)
        if(price1 - price2) < precision or i >= max_iter:
            break
        else:
            init_vol = init_vol - dvol * price2 / (price1 - price2)
            i += 1
    return init_vol


if __name__ == "__main__":
    iv = get_iv_newton(1.8, BlackScholes.TAG_PUT, 5128.22, 4600, 0.026463, 0.174961582, 0.021917808)
    print(iv)