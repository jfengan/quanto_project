from abc import ABC, abstractmethod
from scipy.stats import norm
import math


class DigitalQuanto(ABC):
    def __init__(self, rd, q, rf, sigma_s, sigma_f, rho, t, spot, strike, quanto_factor):
        self.rd = rd
        self.rf = rf
        self.q = q
        self.sigma_s = sigma_s
        self.sigma_f = sigma_f
        self.rho = rho
        self.t = t
        self.spot = spot
        self.strike = strike
        self.quanto_factor = quanto_factor

    @abstractmethod
    def price(self):
        raise NotImplemented


class FloatingFXDigitalQuantoCall(DigitalQuanto):

    def sigma(self) -> float:
        # Because we let the exchange rate be floating, so there's no risk-adjustment for the drift
        # since under fx measure, the payoff is fixed -- 1 fx currency
        # and the floating fx rate could be captured by the fixed forward rate
        return self.sigma_s

    def mu(self) -> float:
        return self.rf - self.q

    def d1(self) -> float:
        return (math.log(self.spot / self.strike) + (self.mu() + .5 * self.sigma() ** 2) * self.t) /\
               (self.sigma() * math.sqrt(self.t))

    def d2(self) -> float:
        return self.d1() - self.sigma() * math.sqrt(self.t)

    def fx_price(self):
        return math.exp(-self.rf * self.t) * norm.cdf(self.d2())

    def price(self):
        return self.fx_price() * self.quanto_factor


class FloatingFXDigitalQuantoPut(FloatingFXDigitalQuantoCall):

    def fx_price(self) -> float:
        return math.exp(-self.rf * self.t) * (1 - norm.cdf(self.d2()))

    def price(self):
        return self.fx_price() * self.quanto_factor


class FloatingDomStrikeDigitalQuantoCall(DigitalQuanto):

    def sigma(self) -> float:
        # If we set fx rate fixed, then there should be an adjust to the risk-neutral probablity
        return math.sqrt(self.sigma_f ** 2 + self.sigma_s ** 2 + 2 * self.rho * self.sigma_f * self.sigma_s)

    def mu(self) -> float:
        return self.rd - self.q

    def d1(self):
        return (math.log(self.spot * self.quanto_factor / self.strike) + (self.mu() + .5 * self.sigma() ** 2) * self.t) \
               / (self.sigma() * math.sqrt(self.t))

    def d2(self):
        return self.d1() - self.sigma() * math.sqrt(self.t)

    def price(self):
        # price in domestic currency
        return math.exp(-self.rd * self.t) * norm.cdf(self.d2())


class FloatingDomStrikeQuantoPut(FloatingDomStrikeDigitalQuantoCall):

    def price(self):
        return math.exp(-self.rd * self.t) * (1 - norm.cdf(self.d2()))


class FXStrikeDigitalQuantoCall(DigitalQuanto):
    def price(self) -> float:
        return 0.


class FXStrikeDigitalQuantoPut(FXStrikeDigitalQuantoCall):
    def price(self) -> float:
        return 1 - super().price()
