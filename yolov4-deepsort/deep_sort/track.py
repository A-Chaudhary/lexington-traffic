# vim: expandtab:ts=4:sw=4
from math import sqrt, fabs


class TrackState:
    """
    Enumeration type for the single target track state. Newly created tracks are
    classified as `tentative` until enough evidence has been collected. Then,
    the track state is changed to `confirmed`. Tracks that are no longer alive
    are classified as `deleted` to mark them for removal from the set of active
    tracks.

    """

    Tentative = 1
    Confirmed = 2
    Deleted = 3


class Track:
    """
    A single target track with state space `(x, y, a, h)` and associated
    velocities, where `(x, y)` is the center of the bounding box, `a` is the
    aspect ratio and `h` is the height.

    Parameters
    ----------
    mean : ndarray
        Mean vector of the initial state distribution.
    covariance : ndarray
        Covariance matrix of the initial state distribution.
    track_id : int
        A unique track identifier.
    n_init : int
        Number of consecutive detections before the track is confirmed. The
        track state is set to `Deleted` if a miss occurs within the first
        `n_init` frames.
    max_age : int
        The maximum number of consecutive misses before the track state is
        set to `Deleted`.
    feature : Optional[ndarray]
        Feature vector of the detection this track originates from. If not None,
        this feature is added to the `features` cache.

    Attributes
    ----------
    mean : ndarray
        Mean vector of the initial state distribution.
    covariance : ndarray
        Covariance matrix of the initial state distribution.
    track_id : int
        A unique track identifier.
    hits : int
        Total number of measurement updates.
    age : int
        Total number of frames since first occurance.
    time_since_update : int
        Total number of frames since last measurement update.
    state : TrackState
        The current track state.
    features : List[ndarray]
        A cache of features. On each measurement update, the associated feature
        vector is added to this list.
    movement : Boolean
        If track is moving with a certain error range output value   

    """

    def __init__(self, mean, covariance, track_id, n_init, max_age, birth,
                 feature=None, class_name=None):
        self.mean = mean
        self.covariance = covariance
        self.track_id = track_id
        self.hits = 1
        self.age = 1
        self.birth = birth
        self.time_since_update = 0

        self.state = TrackState.Tentative
        self.features = []
        if feature is not None:
            self.features.append(feature)

        self._n_init = n_init
        self._max_age = max_age
        self.class_name = class_name

        self.movement = True
        self.position = self.to_xy()
        self.previousPositions = []
        self.displacement = [0,0]
        self.speed = 0
        self.previousSpeeds = []

        self.acceleration = 0
        self.previousAccelerations = []

        self.change = 0

    def to_tlwh(self):
        """Get current position in bounding box format `(top left x, top left y,
        width, height)`.

        Returns
        -------
        ndarray
            The bounding box.

        """
        ret = self.mean[:4].copy()
        ret[2] *= ret[3]
        ret[:2] -= ret[2:] / 2
        return ret

    def to_tlbr(self):
        """Get current position in bounding box format `(min x, miny, max x,
        max y)`.

        Returns
        -------
        ndarray
            The bounding box.

        """
        ret = self.to_tlwh()
        ret[2:] = ret[:2] + ret[2:]
        return ret

    def to_xy(self):
        """Get current position `(center x, center y)`"""
        return self.mean[:2]
    
    def get_class(self):
        return self.class_name

    def get_track_id(self):
        return self.track_id

    def get_birth(self):
        return self.birth

    def get_age(self):
        return self.age

    def get_internal_time(self):
        return self.birth + self.age

    def get_acceleration(self):
        return self.acceleration

    def get_speed(self):
        return self.speed

    def get_previous_accelerations(self):
        return self.previousAccelerations

    def get_previous_speeds(self):
        return self.previousSpeeds

    def get_previous_positions(self):
        return self.previousPositions

    def get_change(self):
        return self.change

    def update_position(self):
        self.previousPositions.append(self.position)
        self.position = self.to_xy()

    def calculate_displacement(self):
        """Calculate Displacement `(x,y)` as a percentage of bounding box dimensions."""
        ret = self.to_tlwh()[2:]
        self.displacement[0] = (self.position[0]-self.previousPositions[-1][0]) / ret[0] * 100
        self.displacement[1] = (self.position[1]-self.previousPositions[-1][1]) / ret[1] * 100

    def calculate_change(self):
        self.change = sqrt(self.displacement[0] **2 + self.displacement[1] **2)

    def calculate_speed(self):
        self.previousSpeeds.append([self.birth + self.age ,self.speed])
        self.speed = sqrt(self.displacement[0]**2 + self.displacement[1]**2) / self.time_since_update

    def calculate_acceleration(self):
        self.previousAccelerations.append([self.birth + self.age,self.acceleration])
        self.acceleration = ((self.speed - self.previousSpeeds[-1][1])/self.time_since_update + self.previousAccelerations[-1][1] )/ 2

    def update_kinematics(self):
        self.update_position() 
        self.calculate_displacement()
        self.calculate_speed()
        self.calculate_acceleration()

        self.calculate_change()

        self.movement = self.change > 1.7 or self.speed > 2 or self.acceleration > 1.2
        # self.movement = self.acceleration - self.previousAccelerations[-1][1]  > 0




    def predict(self, kf):
        """Propagate the state distribution to the current time step using a
        Kalman filter prediction step.

        Parameters
        ----------
        kf : kalman_filter.KalmanFilter
            The Kalman filter.

        """
        self.mean, self.covariance = kf.predict(self.mean, self.covariance)
        self.age += 1
        self.time_since_update += 1

    def update(self, kf, detection):
        """Perform Kalman filter measurement update step and update the feature
        cache.

        Parameters
        ----------
        kf : kalman_filter.KalmanFilter
            The Kalman filter.
        detection : Detection
            The associated detection.

        """

        self.mean, self.covariance = kf.update(
            self.mean, self.covariance, detection.to_xyah())
        self.features.append(detection.feature)

        self.update_kinematics()

        self.hits += 1
        self.time_since_update = 0
        if self.state == TrackState.Tentative and self.hits >= self._n_init:
            self.state = TrackState.Confirmed

        

    def mark_missed(self):
        """Mark this track as missed (no association at the current time step).
        """
        if self.state == TrackState.Tentative:
            self.state = TrackState.Deleted
        elif self.time_since_update > self._max_age:
            self.state = TrackState.Deleted

    def is_moving(self):
        return self.movement

    def is_tentative(self):
        """Returns True if this track is tentative (unconfirmed).
        """
        return self.state == TrackState.Tentative

    def is_confirmed(self):
        """Returns True if this track is confirmed."""
        return self.state == TrackState.Confirmed

    def is_deleted(self):
        """Returns True if this track is dead and should be deleted."""
        return self.state == TrackState.Deleted
