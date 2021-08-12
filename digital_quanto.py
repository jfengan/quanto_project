import math
from abc import ABC, abstractmethod
from scipy.stats import norm


class DigitalQuanto(ABC):
    def __init__(self, spot, strike, t, rho, sigma_spot, sigma_fx, r_quote, r_base, r_dom):
        self.spot = spot
        self.strike = strike
        self.t = t
        self.rho = rho
        self.sigma_spot = sigma_spot
        self.sigma_fx = sigma_fx
        self.r_quote = r_quote
        self.r_base = r_base
        self.r_dom = r_dom

    @abstractmethod
    def price(self):
        raise NotImplemented


class DigitalQuantoCall(DigitalQuanto):

    def sigma_spot_t(self):
        return self.r_base - self.r_quote - self.rho * self.sigma_spot * self.sigma_fx

    def d(self):
        return (math.log(self.spot / self.strike) + (self.sigma_spot_t() - self.sigma_spot ** 2 / 2) * self.t) \
               / (self.sigma_spot * math.sqrt(self.t))

    def price(self):
        return math.exp(-self.r_dom * self.t) * norm.cdf(self.d())


class DigitalQuantoPut(DigitalQuantoCall):

    def price(self):
        return 1 - super().price()


if __name__ == "__main__":
    spot = 106.6
    strike = 110
    t = 1
    rho = -0.2789
    sigma_spot = 0.0855
    sigma_fx = 0.1099
    r_base = 0.025
    r_quote = 0.001
    r_dom = 0.04
    call = DigitalQuantoCall(spot, strike, t, rho, sigma_spot, sigma_fx, r_quote, r_base, r_dom)
    print(1 - call.price())
