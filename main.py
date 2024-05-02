#!/usr/bin/env python3
class main:
	def clear(self, amount):
		for i in range(amount):
			print('\x1b[1A\x1b[2K', end='')

	def downloadVideos(self, link):
		r = requests.get(link, headers = self.headers, cookies = self.cookies, timeout = None)
		if r.status_code == 200:
			link = str(link.split('/')[-1])
			open(f'{self.outputDir}{link}', 'wb').write(r.content)

	def getVideoLinks(self, page):
		if page.startswith('https://') and 'cnn.com' in page:
			r = requests.get(page, headers = self.headers, cookies = self.cookies, timeout = self.args.timeout)
			if r.status_code == 200:
				if '"VideoObject","contentUrl":"' in r.text:
					links = []
					for link in r.text.split('"VideoObject","contentUrl":"'):
						links.append(link.split('"')[0])
					links.pop(0)
					return links
				return
			return False
		print(f'{self.red}[!] Page: {page} does not appear to be a link or it does not reference cnn.com{self.end}')

	def threaded(self, inQueue):
		while not inQueue.empty():
			link = inQueue.get()
			self.stats['count'] += 1
			self.downloadVideos(link)
			inQueue.task_done()

	def statThread(self, *k):
		o = '. '
		c = 0
		while self.stats['count'] <= self.stats['amount']:
			print(f'{self.pink}[*] Downloading videos: ({self.stats["count"]}/{self.stats["amount"]}) may take a few minutes {o * c}{self.end}')
			c += 1
			if c == 4:
				c = 0

			time.sleep(0.5)
			self.clear(1)

	def __init__(self):
		parser = argparse.ArgumentParser(description = 'Simple program to download all videos from a cnn.com article, because nobody else has made one.')
		parser.add_argument('input', help='Should be a cnn.com newspage link which contains video(s) to download, if --file is provided it will be used as the name for a file')
		parser.add_argument('--file', '-f', dest='isFile', action='store_true', help='Use the input as the name of a text file which contains cnn.com links')
		parser.add_argument('--output', '-o', dest='outputDir', action='store', help='A directory to place downloaded video files, the default location will be the current directory')
		parser.add_argument('--timeout', dest='timeout', action='store', const=5, default=5, nargs='?', type=int, help='How long shall we wait when extracting video links from the provided newspage links')
		parser.add_argument('--threads', dest='threadAmount', action='store', const=100, default=100, nargs='?', type=int, help='Maximum amount of threads to use')
		parser.add_argument('--alias', dest='addAlias', action='store_true', help='Add an alias to your .bashrc file')
		self.args = parser.parse_args()
		self.end = '\x1b[0m'
		self.red = '\x1b[38;2;255;0;0m'
		self.green = '\x1b[38;2;0;255;0m'
		self.pink = '\x1b[38;2;255;0;255m'
		self.cookies = {}
		self.headers = {
			"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
			"Accept-Language": "en-GB,en;q=0.5",
			"Accept-Encoding": "gzip, deflate, br",
			"DNT": "1",
			"Connection": "keep-alive",
			"Upgrade-Insecure-Requests": "1",
			"Sec-Fetch-Dest": "document",
			"Sec-Fetch-Mode": "navigate",
			"Sec-Fetch-Site": "none",
			"Sec-Fetch-User": "?1",
			"TE": "trailers"
		}

		if self.args.addAlias:
			home = os.path.expanduser('~')
			if '.bashrc' in os.listdir(home):
				alias = f'alias cnnDL="python3 {os.getcwd()}/main.py"'
				bashrc = open(f'{home}/.bashrc', 'a+')
				bashrc.seek(0)
				if alias not in bashrc.read():
					bashrc.write(alias + '\n')
					print(f'{self.green}[+] Added alias to .bashrc, you need to run "exec bash" to use this{self.end}')
					# os.system('exec bash')

				else:
					print(f'{self.pink}[*] No need to add an alias to .bashrc as it already exists{self.end}')
			else:
				print(f'{self.red}[!] .bashrc was not found in your home directory{self.end}')

		if self.args.isFile:
			if os.path.exists(self.args.input):
				allLinks = []
				for line in set(open(self.args.input, 'r').read().splitlines()):
					links = self.getVideoLinks(line)
					if type(links) == list:
						allLinks += links
			else:
				print(f'{self.red}[!] Input file does not exist{self.end}')
				return
		else:
			allLinks = self.getVideoLinks(self.args.input)

		if self.args.outputDir is not None:
			if not os.path.exists(self.args.outputDir):
				os.makedirs(self.args.outputDir)
			self.outputDir = f'{self.args.outputDir}/'
		else:
			self.outputDir = ''

		if type(allLinks) == list:
			amount = len(allLinks)
			if amount >= 2:
				inputQueue = queue.Queue()

				for link in allLinks:
					inputQueue.put(link)

				if amount >= self.args.threadAmount:
					threads = self.args.threadAmount
				else:
					threads = amount

				self.stats = {
					'count': 0,
					'amount': amount
				}

				try:
					for thread in range(threads + 1):
						print(f'{self.green}[+] Starting Thread: {thread}/{threads}{self.end}')
						if thread == threads:
							threading.Thread(target = self.statThread, daemon = True).start()
						else:
							threading.Thread(target = self.threaded, args = [inputQueue], daemon = True).start()
						self.clear(1)
					inputQueue.join()
				except KeyboardInterrupt:
					print(f'{self.red}[!] Interrupted. {self.red}')

			elif amount == 1:
				print(f'{self.green}[+] Starting download for {allLinks[0]}{self.end}')
				self.downloadVideos(allLinks[0])
				print(f'{self.green}[+] Success!{self.end}')
				time.sleep(0.25)
				self.clear(2)
			else:
				print(f'{self.red}[!] Weird error, returned empty list{self.end}')


if __name__ == '__main__':
	import requests, argparse, os, queue, threading, time
	main()
