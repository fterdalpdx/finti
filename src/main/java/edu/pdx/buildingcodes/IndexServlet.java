package edu.pdx.buildingcodes;

import java.io.File;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.api.client.extensions.appengine.http.UrlFetchTransport;
import com.google.api.client.googleapis.auth.oauth2.GoogleCredential;
import com.google.api.client.googleapis.extensions.appengine.auth.oauth2.AppIdentityCredential;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.api.services.admin.directory.Directory;
import com.google.api.services.admin.directory.DirectoryScopes;
import com.google.appengine.api.users.User;
import com.google.appengine.api.users.UserService;
import com.google.appengine.api.users.UserServiceFactory;

public class IndexServlet extends HttpServlet {

	private static final long serialVersionUID = -478728366061947997L;

	@Deprecated
	static Directory newDirectory() {
		AppIdentityCredential credential = new AppIdentityCredential(
				Arrays.asList(DirectoryScopes.ADMIN_DIRECTORY_USER));
		return new Directory.Builder(new UrlFetchTransport(),
				new JacksonFactory(), credential).setApplicationName(
				"Building Codes").build();
	}

	static Directory newDir() throws GeneralSecurityException, IOException {
		HttpTransport httpTransport = GoogleNetHttpTransport
				.newTrustedTransport();
		JsonFactory jsonFactory = JacksonFactory.getDefaultInstance();
		List<String> scopes = new ArrayList<String>();
		scopes.add(DirectoryScopes.ADMIN_DIRECTORY_USER);
		scopes.add(DirectoryScopes.ADMIN_DIRECTORY_USER_READONLY);
		// Build service account credential.
		// serviceAccountUser should be the person who is logged in.  Or the domain manager if the app is running as a daemon.
		GoogleCredential credential = new GoogleCredential.Builder()
				.setTransport(httpTransport)
				.setJsonFactory(jsonFactory)
				.setServiceAccountId(
						"307368374756-ndt1oea0hvppplmmqgivbblh53dqkuk6@developer.gserviceaccount.com")
				.setServiceAccountScopes(scopes)
				.setServiceAccountUser("billy.paul@williambillypaul.com")
				.setServiceAccountPrivateKeyFromP12File(new File("key.p12"))
				.build();
		// set up global Plus instance
		return new Directory.Builder(httpTransport, jsonFactory, null)
				.setHttpRequestInitializer(credential).build();
	}

	@Override
	public void doGet(HttpServletRequest req, HttpServletResponse resp)
			throws IOException, ServletException {

		UserService userService = UserServiceFactory.getUserService();

		User user = userService.getCurrentUser();
		String authDomain = user.getAuthDomain();
		System.out.println(authDomain);
		System.out.println(user.getFederatedIdentity());
		System.out.println("TESTING++++++++++++++++++++++++++++++++");

		String thisURL = req.getRequestURI();

		if (req.getUserPrincipal() != null) {
			Directory directory = null;
			try {
				directory = newDir();
			} catch (GeneralSecurityException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			List<com.google.api.services.admin.directory.model.User> users = directory
					.users().list().setDomain("williambillypaul.com").execute()
					.getUsers();
			String names = "";
			System.out.println("Size = " + users.size());
			for (com.google.api.services.admin.directory.model.User userModel : users) {
				names += userModel.getName();
			}
			req.setAttribute("names", names);
			req.getRequestDispatcher("/index.jsp").forward(req, resp);
			// resp.setContentType("text/html");
			// resp.getWriter().println(
			// "<p>Hello, " + req.getUserPrincipal().getName()
			// + "!  You can <a href=\""
			// + userService.createLogoutURL(thisURL)
			// + "\">sign out</a>.</p>");
		} else {
			req.getRequestDispatcher("/index.jsp").forward(req, resp);
		}
	}
}
