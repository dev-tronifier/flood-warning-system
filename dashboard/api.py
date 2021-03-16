from flask_restful import Resource, reqparse, abort
from dashboard.models import Device, Data
from dashboard import app, api, db, bcrypt
import datetime

data_args = reqparse.RequestParser()
data_args.add_argument("api_key", type=str, help="API Key is required for authentication", required=True)
data_args.add_argument("data", type=int, help="Data to be added to database is required", required=True)
data_args.add_argument("timestamp", type=str, help="timestamp is required", required=False)

class DataUpdate(Resource):
    def put(self, device_id):
        device = Device.query.filter_by(id=device_id).first()
        if device:
            args = data_args.parse_args()
            if bcrypt.check_password_hash(device.api_key, args['api_key']):
                if args.get('timestamp'):
                    data = Data(data=args['data'],
                                device_id=device_id,
                                timestamp=datetime.datetime.strptime(args['timestamp'], "%Y-%m-%d %H:%M:%S")
                                )
                else:
                    cur_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data = Data(data=args['data'],
                                device_id=device_id,
                                timestamp=datetime.datetime.strptime(cur_time_str, "%Y-%m-%d %H:%M:%S")
                                )
                db.session.add(data)
                db.session.commit()
            else:
                abort({'message':'Invalid API Key', 'success':0})
        else:
            abort({'message':'Invalid device id', 'success':0})

        return {'message':'Data successfully added', 'success':1}, 201