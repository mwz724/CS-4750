Name: Michelle Zhou

NetID: mwz7

Derivation for state update:

Derivation for $$x_t$$:
$$
\begin{align*}
    \frac{dx}{dt} &= v \cos\theta
    \\ dx &= v \cos\theta dt
    \\ \int_{x_{t-1}}^{x_{t}}dx &=\int_{t}^{t+\Delta t} v \cos\theta dt
    \\ x_{t}-x_{t-1} &= \int_{\theta_t}^{\theta_{t+\Delta t}} v \cos\theta \bigg( \frac{L}{v \tan\alpha}\bigg) d\theta 
    \\ x_t &= x_{t-1} + \bigg( \frac{L}{\tan\alpha}\bigg) (\sin\theta_{t+\Delta t} - \sin\theta_{t})
\end{align*}
$$

Derivation for $$y_t$$:
$$
\begin{align*}
    \frac{dy}{dt} &= v \sin\theta
    \\ dy &= v \sin\theta dt
    \\ \int_{y_{t-1}}^{y_{t}}dx &=\int_{t}^{t+\Delta t} v \sin\theta dt
    \\ y_{t}-y_{t-1} &= \int_{\theta_t}^{\theta_{t+\Delta t}} v \sin\theta \bigg( \frac{L}{v \tan\alpha}\bigg) d\theta 
    \\ y_t &= y_{t-1} -\bigg( \frac{L}{\tan\alpha}\bigg) (\cos\theta_{t+\Delta t} - \sin\theta_{t})
\end{align*}
$$

Note: I use the following relationship between $dt$ and $$d\theta$$:
$$
\begin{align*}
    \frac{d\theta}{dt} &= \frac{v}{\tan\alpha}
    \\ \frac{L\tan\alpha}{v}d\theta &= dt
\end{align*}
$$

I found out that using the following representation with $$d\theta$$ in the denominator often led to NaN errors when there was no angular control:
$$
\begin{align*}
    dt &= \frac{dt}{d\theta} d\theta
\end{align*}
$$

