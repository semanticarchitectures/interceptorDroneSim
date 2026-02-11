function d = Distance(a, b)
%DISTANCE Euclidean distance between two 2D points.
    delta = b - a;
    d = hypot(delta(1), delta(2));
end

