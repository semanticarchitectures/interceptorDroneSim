function losRate = LineOfSightRate(posA, velA, posB, velB)
%LINEOFSIGHTRATE Line of sight angular rate in rad/s.
    relPos = posB - posA;
    relVel = velB - velA;
    rSq = dot(relPos, relPos);
    if rSq < 1e-9
        losRate = 0.0;
        return;
    end
    cross2D = relPos(1) * relVel(2) - relPos(2) * relVel(1);
    losRate = cross2D / rSq;
end


