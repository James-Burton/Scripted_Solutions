function convertToRoman(num) {
    const myList = [
        [1000, "M"],
        [500, "D"],
        [100, "C"],
        [50, "L"],
        [10, "X"],
        [5, "V"],
        [1, "I"]
    ];
    let myAnswer = "";
    for (let row in myList) {
        row=Number(row);
        let a = myList[row][0];
        let b = myList[row][1];
        let c = "";
        let d = "";
        let nb='';
        let nv='';
        if (a % 10 === 0&& a.toString().includes('1')) {
            let x = Number(row) + 2;
            c = myList[x][0];
            d = myList[x][1];
        } else if (a % 5 === 0) {
            let x = Number(row) + 1;
            c = myList[x][0];
            d = myList[x][1];

        } else {
            c = a;
            d = b;
        };
        while (num!==0&&num/a>=.8&&(num+c)/a>=1){
            if (num/a<1&&(num+c)/a>=1){
                console.log('a');
                myAnswer+=d;
                num+=c;
                myAnswer+=b;
                num-=a;
            } else if( num/a>=1&&(num+(3*c))/a<1){
                myAnswer+=b;
                if (num/a>=1&&(num-c)/a<=1){
                    myAnswer+=d;num-=c;}
                if (num/a>=1&&num-(2*c)/a<=1){
                    myAnswer+=d+d;num-=c;}
                if (num/a>=1&&num-(3*c)/a<=1){
                    myAnswer+=d+d+d;num-=c;}
                num-=a;
            }else{
                myAnswer+=b;
                num-=a;
            };
        };
    };
    console.log(myAnswer);
    return myAnswer;
}

convertToRoman(2014);
