function target = InitTarget(cfg)
%INITTARGET Build target state struct from configuration.
    target = struct();
    target.name = string(localGet(cfg, "name", "target"));
    target.pos = reshape(localGet(cfg, "position", [3000.0, 1000.0]), 1, 2);
    target.speed = localGet(cfg, "speed", 30.0);
    target.heading = 0.0;
    target.active = true;
    target.rcs = localGet(cfg, "rcs", 0.01);
    target.waypointThreshold = localGet(cfg, "waypoint_threshold", 20.0);

    wps = localGet(cfg, "waypoints", zeros(0, 2));
    if isempty(wps)
        target.waypoints = zeros(0, 2);
    else
        target.waypoints = reshape(wps, [], 2);
    end
    target.currentWaypointIdx = 1;

    if ~isempty(target.waypoints)
        target.heading = utils.Bearing(target.pos, target.waypoints(1, :));
    end
end

function value = localGet(s, fieldName, defaultValue)
    if isfield(s, fieldName)
        value = s.(fieldName);
    else
        value = defaultValue;
    end
end
