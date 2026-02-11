function isHit = CheckIntercept(interceptor, targetPos)
%CHECKINTERCEPT Return true when target is inside kill radius.
    isHit = utils.Distance(interceptor.pos, targetPos) <= interceptor.killRadius;
end
