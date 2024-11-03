"""
Models
"""
import datetime
from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey, DateTime, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from smarthome.connectors.database import Base


class UserToken(Base):
    """ User token db model """
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tokens")
    # Add created / valid

    def __repr__(self):
        return f"<UserToken {self.id}: {self.token}>"


class NodeToken(Base):
    """ Node token db model """
    __tablename__ = "node_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"))
    node = relationship("Node", back_populates="tokens")
    # Add created / valid

    def __repr__(self):
        return f"<NodeToken {self.id}: {self.token}>"


class UserNode(Base):
    """ Connection Node and User db model """
    __tablename__ = "user_nodes"

    node_id = Column(Integer, ForeignKey("nodes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    __table_args__ = (
        PrimaryKeyConstraint("node_id", "user_id"),
        {},
    )

    def __repr__(self):
        return f"<{self.node_id} - {self.user_id}>"


class User(Base):
    """ User db model """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    tokens = relationship("UserToken", back_populates="user")

    # TODO с этим нужно разобраться, как связь правильно делается
    # nodes = relationship('Node', secondary=UserNode.__table__, backref='users.id')
    nodes = relationship('Node', secondary=UserNode.__table__, backref='users_id')

    def __repr__(self):
        return f"<{self.id}: {self.email}>"

    @property
    def bus_id(self):
        # TODO пока так разделяю в редисе ключи пользователя и ноды
        return f"user-{self.id}"


class Node(Base):
    """ Node db model """
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    tokens = relationship("NodeToken", back_populates="node")

    # TODO с этим нужно разобраться, как связь правильно делается
    # users = relationship('User', secondary=UserNode.__table__, backref='nodes.id')
    users = relationship('User', secondary=UserNode.__table__, backref='nodes_id')

    lamps = relationship("NodeLamp", back_populates="node")
    sensors = relationship("NodeSensor", back_populates="node")

    def __repr__(self):
        return f"<{self.id}>"

    @property
    def bus_id(self):
        # TODO пока так разделяю в редисе ключи пользователя и ноды
        return f"node-{self.id}"


class NodeLamp(Base):
    """ Node lamps db model """
    __tablename__ = "node_lamps"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    name = Column(String, index=True)
    value = Column(Integer)
    node_id = Column(Integer, ForeignKey("nodes.id"), index=True)
    node = relationship("Node", back_populates="lamps")
    node_lamp_id = Column(Integer)

    __table_args__ = (
        UniqueConstraint('node_id', 'node_lamp_id'),
    )

    def __repr__(self):
        return f"<{self.id} [{self.node_id}] {self.name}: {self.value}>"


class NodeSensor(Base):
    """ Node sensor db model """
    __tablename__ = "node_sensors"

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    name = Column(String, index=True)
    value = Column(Float)
    node_id = Column(Integer, ForeignKey("nodes.id"), index=True)
    node = relationship("Node", back_populates="sensors")
    node_sensor_id = Column(Integer)

    __table_args__ = (
        UniqueConstraint('node_id', 'node_sensor_id'),
    )

    def __repr__(self):
        return f"<{self.id} [{self.node_id}] {self.name}: {self.value}>"


"""
INIT
insert into users (email, hashed_password) values ('alexey@sharypov.ru', '123');
insert into nodes (url, is_active, is_online) values ('http://192.168.0.103/api', true, false);
insert into node_tokens (token, node_id) values ('test', 1);
insert into user_nodes (user_id, node_id) values (1,1);
insert into node_lamps (name, node_id, value, node_lamp_id) values ('Pin 17', 1, 0, 17);
insert into node_lamps (name, node_id, value, node_lamp_id) values ('Pin 18', 1, 0, 18);
insert into node_sensors (name, node_id, value, node_sensor_id) values ('Temperatura (116)', 1, 0, 116);
insert into node_sensors (name, node_id, value, node_sensor_id) values ('Humidity (216)', 1, 0, 216);

insert into users (email, hashed_password) values ('shvmedia@mail.ru', '123');
"""