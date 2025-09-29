# 🗄️ MongoDB Deployment for AI Ad Copy Generator

## 📋 Quick Deployment

```bash
cd /Users/macbook/Desktop/adcopy/mongo
./deploy-mongo.sh
```

## 🚀 Manual Deployment Steps

### Step 1: Create MongoDB App
```bash
cd /Users/macbook/Desktop/adcopy/mongo
flyctl launch --name adcopy-mongo --region fra --no-deploy
```

### Step 2: Create Volume for Data Persistence
```bash
flyctl volumes create adcopy_mongo_data --region fra --size 1
```

### Step 3: Deploy MongoDB
```bash
flyctl deploy
```

### Step 4: Update Backend Connection
```bash
cd ../backend
flyctl secrets set MONGODB_URL="mongodb://adcopy-mongo.internal:27017/ad_copy_generator" -a adcopy
```

## 🔗 Connection Strings

### For Backend App (Internal Network)
```
mongodb://adcopy-mongo.internal:27017/ad_copy_generator
```

### For External Access
```
mongodb://adcopy-mongo.fly.dev:27017/ad_copy_generator
```

## 🧪 Testing Connection

### Test via Proxy (Local Connection)
```bash
# Start proxy in one terminal
flyctl proxy 27017:27017 -a adcopy-mongo

# Test connection in another terminal
mongosh --host localhost --port 27017 --eval "db.adminCommand('ping')"
```

### Test Direct Connection
```bash
mongosh --host adcopy-mongo.fly.dev --port 27017 --eval "db.adminCommand('ping')"
```

## 📊 Management Commands

```bash
# View MongoDB logs
flyctl logs -a adcopy-mongo

# SSH into MongoDB container
flyctl ssh console -a adcopy-mongo

# Restart MongoDB
flyctl restart -a adcopy-mongo

# Scale MongoDB (if needed)
flyctl scale memory 2048 -a adcopy-mongo

# Check app status
flyctl status -a adcopy-mongo
```

## 🔧 Configuration Details

- **App Name:** `adcopy-mongo`
- **Region:** `fra` (Frankfurt - same as backend)
- **MongoDB Version:** 6.0
- **Memory:** 1GB
- **Volume:** `adcopy_mongo_data` (1GB)
- **Port:** 27017
- **Database:** `ad_copy_generator`

## 🔒 Security Notes

- MongoDB runs on internal Fly.io network
- Only accessible from other Fly.io apps in same organization
- External access requires proxy for security
- No authentication configured (internal network security)

## 📈 Scaling Options

### Increase Storage
```bash
flyctl volumes extend <volume_id> --size 5  # Extend to 5GB
```

### Increase Memory
```bash
flyctl scale memory 2048 -a adcopy-mongo  # Scale to 2GB RAM
```

## 🚨 Troubleshooting

### MongoDB Won't Start
```bash
# Check logs
flyctl logs -a adcopy-mongo

# Restart app
flyctl restart -a adcopy-mongo
```

### Connection Issues
```bash
# Verify app status
flyctl status -a adcopy-mongo

# Test internal connectivity
flyctl ssh console -a adcopy-mongo
# Inside container: mongosh --eval "db.adminCommand('ping')"
```

### Volume Issues
```bash
# List volumes
flyctl volumes list -a adcopy-mongo

# Check volume status
flyctl volumes show <volume_id>
```

## ✅ Success Checklist

- [ ] MongoDB app created and deployed
- [ ] Volume created and mounted
- [ ] Backend updated with MongoDB URL
- [ ] Connection test successful
- [ ] Ad generation saving to database
- [ ] Logs showing successful operations

**🎉 Your MongoDB is now ready for production use!**
