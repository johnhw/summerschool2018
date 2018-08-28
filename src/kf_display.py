import numpy as np

# for interactive drawing
import tkanvas
import pykalman


class KFDisplay(object):
    def __init__(self, A, C, sigma_a, sigma_c, mu_0, sigma_0, path):
        self.track = True
        self.A = A
        self.C = C
        self.sigma_c = sigma_c 
        self.path = iter(path) 
        self.kalman_filter = pykalman.KalmanFilter(
            transition_matrices=A,
            observation_matrices=C,
            transition_covariance=sigma_a,
            observation_covariance=sigma_c,
            initial_state_mean=mu_0,
            initial_state_covariance=sigma_0,
        )
        self.obs_path = []
        self.track_path = []
        self.obs = next(self.path)
        self.src = tkanvas.TKanvas(draw_fn=self.kalman_draw, frame_time=2000, w=800, h=800, bgcolor='black')
        self.mean, self.cov = mu_0, sigma_0
        self.new_mean, self.new_cov = self.kalman_filter.filter_update(self.mean, self.cov, observation=self.obs)
        self.kalman_iter = self.draw_kalman_filter()

        

        
    # Draw each step of the Kalman filter onto a TKinter canvas
    def draw_kalman_filter(self):
        
        self.src.clear()
        font = ("Arial", 24)
        for p in self.obs_path:
            self.src.circle(p[0], p[1], 2, fill="white")
        for p in self.track_path:
            self.src.circle(p[0], p[1], 2, fill="blue")
        if self.obs is not None:
            self.obs_path.append(self.obs)
        self.track_path.append(self.new_mean[:2])
        # don't bother drawing circles when at speed
        
        # draw the prior
        self.src.normal(self.mean[:2], self.cov[:2, :2], outline="#0000ff")
        if self.src.frame_time<50:
            return 
        text = self.src.text(20, 20, text="Prior P(X_t)", anchor="w", fill="gray", font=font)
        self.src.to_front(text)
        yield 0  # this is a trick to allow to "return" here but resume later
        ax = np.dot(self.A, self.mean)
        acov = np.dot(np.dot(self.A, self.cov), self.A.T)
        # prediction after linear dynamics
        self.src.normal(ax[:2], acov[:2, :2], outline="#00ff00", dash=(2, 4))
        self.src.modify(text, text="Prediction f(x_(t-1)) -> x_t")
        self.src.to_front(text)
        yield 0
        # prediction after linear dynamics
        self.src.normal(ax[:2], acov[:2, :2], outline="#dd00ff", dash=(2, 2))
        self.src.modify(text, text="Expected observation y_t g(x_t) -> y'_t")
        self.src.to_front(text)
        yield 0
        if self.obs is not None:
            # observation (if there is one)
            self.src.circle(self.obs[0], self.obs[1], 5, fill="#ffffff")
            # src.modify(text, text="Observation y_t")
            # uncertainty of observation
            self.src.normal(self.obs, self.sigma_c[:2, :2], outline="#6600ff", dash=(2, 2))
            self.src.modify(text, text="Observation w/uncertainty")
            self.src.to_front(text)
            yield 0
            yield 0
        # posterior
        self.src.normal(self.new_mean[:2], self.new_cov[:2, :2], outline="#8899ff")
        self.src.modify(text, text="Posterior P(Xt|Yt)")
        self.src.to_front(text)
        yield 0

    # draw the Kalman filter updates interactively


    def kalman_draw(self, src):
        
        
        if self.src.frame_time > 20:
            # slowly speed up over time
            self.src.frame_time = src.frame_time * 0.95
        try:
            next(self.kalman_iter)
        # we've drawn all the steps, so make another update
        except StopIteration:
            self.mean, self.cov = self.new_mean, self.new_cov
            self.new_mean, self.new_cov = self.kalman_filter.filter_update(self.mean, self.cov, observation=self.obs)
            self.kalman_iter = self.draw_kalman_filter()
            try:
                self.obs = next(self.path)
           
            except StopIteration:
                src.quit(None)
            return
