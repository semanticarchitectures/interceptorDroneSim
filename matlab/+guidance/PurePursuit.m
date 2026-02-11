function cmdHeading = PurePursuit(interceptorPos, targetPos)
%PUREPURSUIT Point directly at target.
    cmdHeading = utils.Bearing(interceptorPos, targetPos);
end


