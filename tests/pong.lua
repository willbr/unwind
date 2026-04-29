-- pico-8 style pong
ball_x = 64
ball_y = 64
ball_dx = 1
ball_dy = 1

p1_y = 56
p2_y = 56
p1_score = 0
p2_score = 0

function _init()
    cls()
end

function _update()
    if btn(2) then p1_y = p1_y - 2 end
    if btn(3) then p1_y = p1_y + 2 end

    if ball_y < p2_y + 4 then p2_y = p2_y - 1 end
    if ball_y > p2_y + 4 then p2_y = p2_y + 1 end

    ball_x = ball_x + ball_dx
    ball_y = ball_y + ball_dy

    if ball_y < 0 or ball_y > 127 then
        ball_dy = -ball_dy
    end

    if ball_x < 4 and ball_y > p1_y and ball_y < p1_y + 8 then
        ball_dx = -ball_dx
    end

    if ball_x > 123 and ball_y > p2_y and ball_y < p2_y + 8 then
        ball_dx = -ball_dx
    end

    if ball_x < 0 then
        p2_score = p2_score + 1
        ball_x = 64
        ball_y = 64
    end

    if ball_x > 127 then
        p1_score = p1_score + 1
        ball_x = 64
        ball_y = 64
    end
end

function _draw()
    cls()
    rectfill(2, p1_y, 3, p1_y + 8, 7)
    rectfill(124, p2_y, 125, p2_y + 8, 7)
    pset(ball_x, ball_y, 7)
    print(p1_score, 30, 2, 7)
    print(p2_score, 94, 2, 7)
end
