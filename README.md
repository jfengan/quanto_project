# quanto_project
- research project for digital quanto option

> **Floating FX-strike digital quanto**

$$
c(S, F, T) = F_{T} * Digital(max(S - K, 0)) 
$$

The payoff could be regarded as a vanilla digital quanto option with a forward rate agreement (with price 0￥), which is used to convert the fx into dom ccy at time T

So that the floating fx-strike digital quanto is free of exchange risk and correlation risk

$$
c(S, F, 0) = E[Digital(c(S, F, T))] = F_{0} * Digital(max(S - K, 0)) = F_{0} * N(d2)
$$

***The calculation of d2 is totally under fx asset measure, there's no quanto adjustment to the risk-neutral probability***



> **Domestic-strike option with floating fx rate to deliver**



The drift term of the price process would be:

$$
\mu_{S^*} = r_d - q_d = r_d - q
$$
S* --> fx asset dominated in domestic ccyra

$$
\sigma_{S^*}^2 = \sigma_{S*F}^2 = \sigma_{S} ^ 2 + \sigma_{F} ^ 2 + 2 \rho \sigma_{S} \sigma_{F}
$$

So that
$$
c(S^*, T, K_d) = max(S^* - K_d, 0) \\
= e^{-r_d  \tau} * N(d_2)
$$

where: 
$$
d_1 = \frac{\log{\frac{S^*}{X_d}} + (\mu^d_{S^*} + \frac{\sigma_{S^*}}{2})  \tau}{\sigma_{S^*} \sqrt{\tau}}
$$

$$
d_2 = d_1 - \sigma_{S^*}  \sqrt{\tau}
$$

***The risk-neutral probability is adjusted w.r.t the correlation risk, and since no fx denominated asset is involved in the price process, so rf is not involved in the analytical solution***



> **Fixed Rate Digital Quanto Option**



The payoff of the fixed fx rate quanto digital option should be like:

$$
payoff(S, T, K) = F_0 max(S - K, 0)
$$

where S and K are denominated in foreign currency

Our goal is to find the mu and sigma for assets denominated in foreign currency under domestic risk neutral measure Qd

For the very asset denominated in dom currency, because we let the fx rate be fixed, so that the correlation risk should be included into the drift term

$$
\frac{dS_t}{S_t} = \mu^d_{S} dt + \sigma_SdW^d_S
$$

$$
\frac{dF_t}{F_t} = \mu^d_{F} dt + \sigma_FdW_F^d
$$

$$
\mu^d_{S^*} = \mu^d_{FS} = \mu^d_F + \mu^d_S + \rho \sigma_F \sigma_S
$$

$$
\mu^d_S = \mu^d_{S^*} - \mu^d_F - \rho \sigma_F \sigma_S
= r_f - q - \rho \sigma_F \sigma_S
$$



***The diffusion term will not be influenced since the asset is still denominated in foreign currency. The risk-neutral probablity is adjusted w.r.t both exchange risk and correlation risk***