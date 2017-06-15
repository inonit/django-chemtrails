/**
 * Render the Textarea as a Cypher editor.
 */

'use strict';
;(function ($) {
  $(document).ready(function() {
    CodeMirror.fromTextArea(document.getElementById('id_cypher_statement'), {
      mode: 'cypher',
      theme: 'neo',
      tabMode: 'indent',
      indentUnit: 4,
      lineNumbers: true,
      lineWrapping: true,
      matchBrackets: true
    });
  });
})(django.jQuery);

