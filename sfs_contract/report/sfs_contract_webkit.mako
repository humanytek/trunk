<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <%page expression_filter="entity"/>
    <%
    def carriage_returns(text):
        return text.replace('\n', '<br />')
    %>
    %for contract in objects:
           <table class="description" style="font-size:12;font-family: Verdana;">
            %if contract.agreement_template: 
             %for condition in contract.agreement_template.split('\n'):
                <tr><td style="padding-left:35px;font-family: Verdana;font-size:12;">${condition or ''}</td></tr>
             %endfor
            %endif
          </table>
    %endfor
</body>
</html>
