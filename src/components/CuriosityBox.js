import { Avatar } from "@material-ui/core";
import React from "react";
import { useSelector } from "react-redux";
import { selectUser } from "../features/userSlice";
import "./CuriosityBox.css";

export default function CuriosityBox() {
  const user = useSelector(selectUser);

  return (
    <div className="CuriosityBox">
      <div className="CuriosityBox__info">
        <Avatar
          src={
            user.photo
              ? user.photo
              : ""
          }
          className="CuriosityBox__infoAvatar"
        />
        <h5>{user.displayName ? user.displayName : user.email}</h5>
      </div>
      <div className="CuriosityBox__Curiosity">
        <p>What is your question or link?</p>
      </div>
    </div>
  );
}
