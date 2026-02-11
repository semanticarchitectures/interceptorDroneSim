function interceptor = InitInterceptor(cfg)
%INITINTERCEPTOR Build interceptor state struct from configuration.
    interceptor = struct();
    interceptor.name = string(localGet(cfg, "name", "interceptor"));
    interceptor.pos = reshape(localGet(cfg, "position", [200.0, -300.0]), 1, 2);
    interceptor.speed = 0.0;
    interceptor.heading = 0.0;
    interceptor.maxSpeed = localGet(cfg, "max_speed", 80.0);
    interceptor.maxTurnRate = deg2rad(localGet(cfg, "max_turn_rate_deg", 25.0));
    interceptor.killRadius = localGet(cfg, "kill_radius", 5.0);
    interceptor.maxFlightTime = localGet(cfg, "max_flight_time", 90.0);
    interceptor.flightTime = 0.0;
    interceptor.active = true;
    interceptor.state = "READY";

    seekerCfg = localGet(cfg, "seeker", struct());
    interceptor.seeker = models.InitSensor(seekerCfg);
end

function value = localGet(s, fieldName, defaultValue)
    if isfield(s, fieldName)
        value = s.(fieldName);
    else
        value = defaultValue;
    end
end
