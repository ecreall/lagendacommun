var jQuery = require('jquery')
global.$ = jQuery
global.jQuery = jQuery

require('bootstrap')
require('./calendar.js')
require('jquery.placeholder')
jQuery('input, textarea').placeholder()
require('jquery.cookie')
