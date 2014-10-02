package edu.pdx.buildingcodes;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.appengine.api.users.User;
import com.google.appengine.api.users.UserService;
import com.google.appengine.api.users.UserServiceFactory;

public class IndexServlet extends HttpServlet {

	@Override
	public void doGet(HttpServletRequest req, HttpServletResponse resp)
			throws IOException, ServletException {

		Boolean isJSPRequest = Boolean
				.valueOf(req.getParameter("isJSPRequest"));
		if (isJSPRequest.equals(Boolean.FALSE)) {
			UserService userService = UserServiceFactory.getUserService();

			User user = userService.getCurrentUser();

			String thisURL = req.getRequestURI();

			resp.setContentType("text/html");
			if (req.getUserPrincipal() != null) {
				resp.getWriter().println(
						"<p>Hello, " + req.getUserPrincipal().getName()
								+ "!  You can <a href=\""
								+ userService.createLogoutURL(thisURL)
								+ "\">sign out</a>.</p>");
			} else {
				resp.getWriter().println(
						"<p>Please <a href=\""
								+ userService.createLoginURL(thisURL)
								+ "\">sign in</a>.</p>");
			}
		} else {
			req.setAttribute("testatt", "Bob");
			req.getRequestDispatcher("/index.jsp").forward(req, resp);
		}
	}
}
