from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from .. import db
from ..models import User
from ..schemas import UserSchema, UserRegisterSchema, UserLoginSchema

blp = Blueprint(
    "Auth",
    "auth",
    url_prefix="/auth",
    description="Authentication endpoints for users (signup, login, profile)",
)


@blp.route("/signup")
class SignUp(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserSchema)
    def post(self, args):
        """Register a new user. Returns basic user data.
        ---
        summary: User registration
        description: Create a new user account with email and password.
        tags:
          - Auth
        """
        user = User(email=args["email"], name=args.get("name"))
        user.set_password(args["password"])
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Email already registered"}, 400
        return user


@blp.route("/login")
class Login(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, args):
        """Log in and receive a JWT access token.
        ---
        summary: User login
        description: Verify credentials and return a JWT access token.
        tags:
          - Auth
        responses:
          200:
            description: Successful login
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    access_token:
                      type: string
                      description: JWT access token
        """
        email = args["email"]
        password = args["password"]
        user: User | None = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {"message": "Invalid email or password"}, 401

        token = create_access_token(identity=user.id)
        return {"access_token": token}, 200


@blp.route("/me")
class Me(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self):
        """Get the current user's profile.
        ---
        summary: Get profile
        description: Returns basic profile information for the authenticated user.
        tags:
          - Auth
        """
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return user

    @jwt_required()
    @blp.arguments(UserRegisterSchema(partial=True))
    @blp.response(200, UserSchema)
    def patch(self, args):
        """Update profile fields (name or password).
        ---
        summary: Update profile
        description: Update the authenticated user's profile fields.
        tags:
          - Auth
        """
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        name = args.get("name")
        if name is not None:
            user.name = name

        password = args.get("password")
        if password:
            user.set_password(password)

        db.session.commit()
        return user
