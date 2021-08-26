import logging
import torch
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct


def gp(X, y, alpha):

    not_fit = True
    max_iteration = 20
    iteration = 0
    while not_fit:
        try:
            kernel = DotProduct(sigma_0=0, sigma_0_bounds="fixed")
            gpr = GaussianProcessRegressor(kernel=kernel, random_state=0, alpha=alpha)
            gpr = gpr.fit(X, y)

            vec = torch.diag(torch.ones(X.shape[1]))
            mean, std = gpr.predict(vec, return_std=True)


            mean = torch.as_tensor(mean, dtype=torch.get_default_dtype()).reshape([-1])
            # ignore all the off-diagonal terms
            std = torch.as_tensor(std, dtype=torch.get_default_dtype()).reshape([-1])
            likelihood = gpr.log_marginal_likelihood()

            res = torch.sqrt(torch.square(torch.matmul(X, mean.reshape([-1, 1]))-y).mean())

            logging.debug(f"GP fitting: alpha {alpha}:\n"
                          f"            residue {res}\n"
                          f"            mean {mean} std {std}\n"
                          f"            log marginal likelihood {likelihood}")
            not_fit = False

        except Exception as e:
            alpha = alpha *2
            iteration += 1
            logging.debug(f"GP fitting failed for {e.args}; \n"
                          f"           increase alpha to {alpha}")
            if iteration < max_iteration:
                raise ValueError(f"Please set the per species shift and scale to zeros and ones. \n"
                                 "The dataset energy is to diverge to be solved with GP")

    return mean, std
