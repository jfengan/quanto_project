from abc import ABC, abstractmethod
from scipy.stats import norm
import math



class DigitalQuanto(ABC):
    def __init__(self, rs, q, rf, sigma_s, sigma_f, rho, t, spot, strike, quanto_factor):
        self.rs = rs
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

    def dom_drift(self):
        # Because we let the exchange rate be floating, so there's no risk-adjustment for the drift
        # since under fx measure, the payoff is fixed -- 1 fx currency
        return self.rs - self.q - 0.5 * self.sigma_s ** 2

    def d1(self):
        return (math.log(self.spot / self.strike) + self.dom_drift() * self.t) / (self.sigma_s * math.sqrt(self.t))

    def price(self):
        return math.exp(-self.rf * self.t) * norm.cdf(self.d1())


class FloatingFXDigitalQuantoPut(FloatingFXDigitalQuantoCall):

    def price(self):
        return 1 - super(FloatingFXDigitalQuantoPut, self).price()


class FixedFXDigitalQuantoCall(DigitalQuanto):

    def dom_drift(self):
        return self.rs - self.q - 0.5 * self.sigma_s ** 2

    def price(self):
        return

    
class FixedFXDigitalQuantoPut(DigitalQuanto):

    def price(self):
        return 1 - super(FixedFXDigitalQuantoPut, self).price()


if __name__ == "__main__":
    spot = 106
    strike = 110
    tau = 0.5
    q = 0.
    rs = 0.04
    rf = 0.05
    sigma_s = 0.4
    sigma_f = 0.08
    rho = -0.1

    ffdqcall = FloatingFXDigitalQuantoCall(rs, q, rf, sigma_s, sigma_f, rho, tau, spot, strike, "")
    print(ffdqcall.price())
