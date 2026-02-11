function interceptor = StepInterceptor(interceptor, dt)
%STEPINTERCEPTOR Advance interceptor state and position.
    if ~(interceptor.state == "LAUNCHED" || interceptor.state == "TERMINAL")
        return;
    end

    interceptor.flightTime = interceptor.flightTime + dt;
    if interceptor.flightTime >= interceptor.maxFlightTime
        interceptor.state = "MISSED";
        interceptor.speed = 0.0;
        interceptor.active = false;
        return;
    end

    interceptor.pos = interceptor.pos + interceptor.speed * utils.UnitVector(interceptor.heading) * dt;
end
