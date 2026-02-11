function vc = ClosingSpeed(posA, velA, posB, velB)
%CLOSINGSPEED Closing speed along line of sight (positive means closing).
    los = posB - posA;
    losDist = norm(los);
    if losDist < 1e-9
        vc = 0.0;
        return;
    end
    losUnit = los / losDist;
    vc = dot(velA - velB, losUnit);
end


