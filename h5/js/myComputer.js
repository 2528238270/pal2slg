/*
function computerZhao(map, color) {
    let count = 0;
    let destPoint = [-1, -1];
    while (true) {
        count++;
        if (count >= 99999999)
            break;

        let destX = randomInt(0, 14);
        let destY = randomInt(0, 14);
        if (map.data[destX][destY] !== 0)
            continue;

        destPoint = [destX][destY];
        break;
    }
    return destPoint;
}*/

/*
* 五子棋AI算法：
*   1.遍历整个棋盘，对每个可落子点进行评分
*   2.获取评分最大的点
*
* 评分规则：
*   暂无
*
*
* */
function computerZhao(map, color) {
    let ourScore = Array2D(15, 15);
    let hisScore = Array2D(15, 15);
    let ourColor = color;
    let hisColor = 3 - color;

    for (let x = 0; x < 15; x++) {
        for (let y = 0; y < 15; y++) {

        }
    }
}

/*
*   功能：
*       返回4个9元组（4*9的二维数组）
*   返回值：
*       比如：[-1,-1,1,1,1,0,1,2,0]
*       -1:越界
*       0:空
*       1:黑
*       2:白
* */
function lineMap(map, x, y) {
    let offsetMap = [
        [0, 1],     //上、下方向
        [1, 0],     //左、右方向
        [1, 1],    //上左、下右方向
        [1, -1],    //上右、下左方向
    ];
    let result = [];      //返回值

    for (let dir = 0; dir < 4; dir++) {
        let temp = [];
        let offset = offsetMap[dir];
        for (let i = -4; i <= 4; i++) {
            let destX = x + offset[0] * i;
            let destY = y + offset[1] * i;
            if (!notCross(destX, destY)) {
                temp.push(-1);
                console.log("dir:" + dir + " i:" + i + " destX:" + destX + " destY:" + destY);
                continue;
            }
            temp.push(map.data[destX][destY]);
        }
        result.push(temp);
    }
    return result;
}