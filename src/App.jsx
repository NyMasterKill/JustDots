import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/Notifications';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import { Main } from './components/layouts/Main';
import { Customer } from './components/layouts/Customer';
import { TaskCreator } from './components/customer/TaskCreator';
import { MyTasks } from './components/MyTasks';
import { TaskViewer } from './components/tasks/TaskViewer.jsx';
import { Freelancer } from './components/layouts/Freelancer';
import { PublicTasks } from './components/freelancer/PublicTasks.jsx';
import {Moderator} from "./components/layouts/Moderator.jsx";
import ModerateOrders from "./components/moderator/ModerateOrders.jsx";
import Loader from "./components/Loader.jsx";
import Landing from "./components/Landing.jsx";

const App = () => {
  return (
    <NotificationProvider>
      <AuthProvider>
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<Landing/>}/>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route element={<Main />}>
              <Route path="/profile/:id" element={<Profile />} />
              <Route element={<Customer />}>
                <Route path="/create" element={<TaskCreator />} />
              </Route>
              <Route element={<Freelancer />}>
                <Route path="/orders" element={<PublicTasks />} />
              </Route>
              <Route path="/mytasks" element={<MyTasks />} />
              <Route path="/task/:id" element={<TaskViewer />} />
            </Route>
            <Route element={<Moderator/>}>
              <Route path="/moderate" element={<ModerateOrders/>}></Route>
            </Route>
          </Routes>
        </Router>
      </AuthProvider >
    </NotificationProvider>
  );
};

export default App;