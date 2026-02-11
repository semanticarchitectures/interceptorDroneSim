function ang = Bearing(fromPt, toPt)
%BEARING Bearing angle from fromPt to toPt in radians.
    delta = toPt - fromPt;
    ang = atan2(delta(2), delta(1));
end

