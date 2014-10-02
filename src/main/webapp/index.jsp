<%@ page contentType="text/html;charset=UTF-8" language="java"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ page import="com.google.appengine.api.users.UserServiceFactory" %>
<%@ page import="com.google.appengine.api.users.UserService" %>
<%@ page import="com.google.appengine.api.users.User" %>

<html>

<head>
<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
<script type="text/javascript" src="jquery-1.11.1.min.js"></script>
</head>

<body>
   <%
   
     UserService userService = UserServiceFactory.getUserService();
     User user = null;
     if (!userService.isUserLoggedIn()) {
   %>
      Please <a href="<%= userService.createLoginURL("/newlogin.jsp") %>">log in</a>
   <% } else {
      user = userService.getCurrentUser();
      %>
      Welcome, <%= user.getNickname() %>!
        (<a href="<%=userService.createLogoutURL("/") %>">log out</a>)
   <%
     }
   %>
   <br/>
<%
  if (user != null) {
%>
Hello <%= user.getNickname() %>!
<%
  } else {
%>
Hello Blank!
<%
  }
%>
<br/>
<c:set var="user" value="user"></c:set>
<c:choose>
<c:when test="${user != null}">
Hello <%= user.getNickname() %>!
</c:when>
<c:otherwise>
Hello BLANK!
</c:otherwise>
</c:choose>
</body>

</html>