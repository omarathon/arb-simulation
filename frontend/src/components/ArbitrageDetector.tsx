export const detectArbitrage = (matchOdds: any[]): boolean => {
    let minArbValue = Infinity;
  
    for (let i = 0; i < matchOdds.length; i++) {
      for (let j = 0; j < matchOdds.length; j++) {
        if (i === j) continue; // Skip same bookmaker
  
        const homeWin = matchOdds[i].odds?.home_win;
        const awayWin = matchOdds[j].odds?.away_win;
  
        if (homeWin && awayWin) {
          const arbitrageValue = (1 / homeWin) + (1 / awayWin);
          minArbValue = Math.min(minArbValue, arbitrageValue);
        }
      }
    }
  
    return minArbValue < 1;
  };
  