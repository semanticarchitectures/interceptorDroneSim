function wrapped = WrapAngle(angleRad)
%WRAPANGLE Wrap angle to [-pi, pi].
    wrapped = mod(angleRad + pi, 2*pi) - pi;
end

