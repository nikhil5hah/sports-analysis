// Tennis scoring utilities

export const getTennisGameScore = (pointsMe, pointsOpponent) => {
  const scores = ['0', '15', '30', '40'];

  // Handle deuce and advantage
  if (pointsMe >= 3 && pointsOpponent >= 3) {
    if (pointsMe === pointsOpponent) {
      return { me: 'Deuce', opponent: 'Deuce' };
    } else if (pointsMe > pointsOpponent) {
      return { me: 'Adv', opponent: '' };
    } else {
      return { me: '', opponent: 'Adv' };
    }
  }

  return {
    me: scores[Math.min(pointsMe, 3)],
    opponent: scores[Math.min(pointsOpponent, 3)]
  };
};

export const isGameWon = (pointsMe, pointsOpponent) => {
  // Need at least 4 points and win by 2
  if (pointsMe >= 4 && pointsMe - pointsOpponent >= 2) {
    return 'me';
  }
  if (pointsOpponent >= 4 && pointsOpponent - pointsMe >= 2) {
    return 'opponent';
  }
  return null;
};

export const isSetWon = (gamesMe, gamesOpponent) => {
  // Win by reaching 6 with 2-game lead
  if (gamesMe >= 6 && gamesMe - gamesOpponent >= 2) {
    return 'me';
  }
  if (gamesOpponent >= 6 && gamesOpponent - gamesMe >= 2) {
    return 'opponent';
  }
  // Win at 7-5
  if (gamesMe === 7 && gamesOpponent === 5) {
    return 'me';
  }
  if (gamesOpponent === 7 && gamesMe === 5) {
    return 'opponent';
  }
  return null;
};

export const isTiebreaker = (gamesMe, gamesOpponent) => {
  return gamesMe === 6 && gamesOpponent === 6;
};

export const isTiebreakWon = (pointsMe, pointsOpponent) => {
  // Win by reaching 7 with 2-point lead
  if (pointsMe >= 7 && pointsMe - pointsOpponent >= 2) {
    return 'me';
  }
  if (pointsOpponent >= 7 && pointsOpponent - pointsMe >= 2) {
    return 'opponent';
  }
  return null;
};

export const isMatchWon = (setsMe, setsOpponent, bestOf) => {
  const setsToWin = Math.ceil(bestOf / 2); // 2 for best-of-3, 3 for best-of-5
  if (setsMe >= setsToWin) {
    return 'me';
  }
  if (setsOpponent >= setsToWin) {
    return 'opponent';
  }
  return null;
};

export const formatSetScores = (setScores) => {
  return setScores.map(set => `${set.me}-${set.opponent}`).join(' ');
};
