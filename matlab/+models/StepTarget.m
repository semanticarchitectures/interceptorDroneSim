function target = StepTarget(target, dt)
%STEPTARGET Advance target state by one time step.
    if ~target.active
        return;
    end

    if ~isempty(target.waypoints) && target.currentWaypointIdx <= size(target.waypoints, 1)
        wp = target.waypoints(target.currentWaypointIdx, :);
        target.heading = utils.Bearing(target.pos, wp);
        if utils.Distance(target.pos, wp) < target.waypointThreshold
            target.currentWaypointIdx = target.currentWaypointIdx + 1;
        end
    end

    target.pos = target.pos + target.speed * utils.UnitVector(target.heading) * dt;
end
