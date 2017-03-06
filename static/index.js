$(document).ready(function() {
  $('#predict-button').click(function() {
    // get the data in the form
    var minute = $('#minute-input').val();
    if (!isInt(minute)) {
      alert("Please put a non-negative integer for minute");
      return;
    } else {
      minute = parseInt(minute)
    }
    var second = $('#second-input').val();
    if (!isInt(second)) {
      alert("Please put a non-negative integer for second");
      return;
    } else {
      second = parseInt(second)
    }
    var time = (60 * minute + second) * 1000;

    // gold
    var blueGold = $('#blue-gold-input').val()
    if (!isInt(blueGold)) {
      alert("Please put a non-negative integer for blue team's gold");
      return;
    } else {
      blueGold = parseInt(blueGold)
    }
    var purpleGold = $('#purple-gold-input').val()
    if (!isInt(purpleGold)) {
      alert("Please put a non-negative integer for Purple team's gold");
      return;
    } else {
      purpleGold = parseInt(purpleGold)
    }

    // // tower turrets destroyed
    var blueTurretsKilled = $('#blue-turrets-killed-input').val()
    if (!isInt(blueTurretsKilled)) {
      alert("Please put a non-negative integer for blue team's turrets destroyed");
      return;
    } else {
      blueTurretsKilled = parseInt(blueTurretsKilled)
    }
    var purpleTurretsKilled = $('#purple-turrets-killed-input').val()
    if (!isInt(purpleTurretsKilled)) {
      alert("Please put a non-negative integer for Purple team's turrets destroyed");
      return;
    } else {
      purpleTurretsKilled = parseInt(purpleTurretsKilled)
    }

    // inhibitors destroyed
    var blueInhibitorsKilled = $('#blue-inhibitors-killed-input').val()
    if (!isInt(blueInhibitorsKilled)) {
      alert("Please put a non-negative integer for blue team's inhibitors destroyed");
      return;
    } else {
      blueInhibitorsKilled = parseInt(blueInhibitorsKilled)
    }
    var purpleInhibitorsKilled = $('#purple-inhibitors-killed-input').val()
    if (!isInt(purpleInhibitorsKilled)) {
      alert("Please put a non-negative integer for Purple team's inhibitors destroyed");
      return;
    } else {
      purpleInhibitorsKilled = parseInt(purpleInhibitorsKilled)
    }

    // dragons killed
    var blueDragonsKilled = $('#blue-dragons-killed-input').val()
    if (!isInt(blueDragonsKilled)) {
      alert("Please put a non-negative integer for blue team's dragons killed");
      return;
    } else {
      blueDragonsKilled = parseInt(blueDragonsKilled)
    }
    var purpleDragonsKilled = $('#purple-dragons-killed-input').val()
    if (!isInt(purpleDragonsKilled)) {
      alert("Please put a non-negative integer for Purple team's dragons killed");
      return;
    } else {
      purpleDragonsKilled = parseInt(purpleDragonsKilled)
    }

    // barons killed
    var blueBaronsKilled = $('#blue-barons-killed-input').val()
    if (!isInt(blueBaronsKilled)) {
      alert("Please put a non-negative integer for blue team's barons killed");
      return;
    } else {
      blueBaronsKilled = parseInt(blueBaronsKilled)
    }
    var purpleBaronsKilled = $('#purple-barons-killed-input').val()
    if (!isInt(purpleBaronsKilled)) {
      alert("Please put a non-negative integer for Purple team's barons killed");
      return;
    } else {
      purpleBaronsKilled = parseInt(purpleBaronsKilled)
    }

    // kills
    var blueKills = $('#blue-kills-input').val()
    if (!isInt(blueKills)) {
      alert("Please put a non-negative integer for blue team's kills");
      return;
    } else {
      blueKills = parseInt(blueKills)
    }
    var purpleKills = $('#purple-kills-input').val()
    if (!isInt(purpleKills)) {
      alert("Please put a non-negative integer for Purple team's kills");
      return;
    } else {
      purpleKills = parseInt(purpleKills)
    }

    // assists
    var blueAssists = $('#blue-assists-input').val()
    if (!isInt(blueAssists)) {
      alert("Please put a non-negative integer for blue team's assists");
      return;
    } else {
      blueAssists = parseInt(blueAssists)
    }
    var purpleAssists = $('#purple-assists-input').val()
    if (!isInt(purpleAssists)) {
      alert("Please put a non-negative integer for Purple team's assists");
      return;
    } else {
      purpleAssists = parseInt(purpleAssists)
    }

    // deaths
    var blueDeaths = $('#blue-deaths-input').val()
    if (!isInt(blueDeaths)) {
      alert("Please put a non-negative integer for blue team's deaths");
      return;
    } else {
      blueDeaths = parseInt(blueDeaths)
    }
    var purpleDeaths = $('#purple-deaths-input').val()
    if (!isInt(purpleDeaths)) {
      alert("Please put a non-negative integer for Purple team's deaths");
      return;
    } else {
      purpleDeaths = parseInt(purpleDeaths)
    }

    $.ajax({
      url: '/predict',
      type: 'GET',
      data: {
        'time': time,
        'blueGold': blueGold,
        'purpleGold': purpleGold,
        'blueTurretsKilled': blueTurretsKilled,
        'purpleTurretsKilled': purpleTurretsKilled,
        'blueInhibitorsKilled': blueInhibitorsKilled,
        'purpleInhibitorsKilled': purpleInhibitorsKilled,
        'blueDragonsKilled': blueDragonsKilled,
        'purpleDragonsKilled': purpleDragonsKilled,
        'blueBaronsKilled': blueBaronsKilled,
        'purpleBaronsKilled': purpleBaronsKilled,
        'blueKills': blueKills,
        'purpleKills': purpleKills,
        'blueAssists': blueAssists,
        'purpleAssists': purpleAssists,
        'blueDeaths': blueDeaths,
        'purpleDeaths': purpleDeaths
      },
      success: function(data) {
        $('#prediction-div').empty()
        $('#prediction-div').append('<p style="color: blue;">Probability of blue winning: ' + data['blueWinProbability'] + '</p>' + 
          '<p style="color: purple">Probability of purple winning: ' + data['purpleWinProbability'] + '</p>')
      },
      error: function(err) {
        alert('Woops! Could not compute the probability. Sorry.')
      }
    });
  });
});

var isInt = function(st) {
  return st.match(/^\d+$/)
};